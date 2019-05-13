#!/usr/bin/env python
# encoding: utf-8
"""
ecoclassifier.py

Created by Pierre-Julien Grizel et al.
Copyright (c) 2016 NumeriCube. All rights reserved.

Main eco-classifier entry point
"""
from __future__ import unicode_literals

__author__ = ""
__copyright__ = "Copyright 2016, NumeriCube"
__credits__ = ["Pierre-Julien Grizel"]
__license__ = "CLOSED SOURCE"
__version__ = "TBD"
__maintainer__ = "Pierre-Julien Grizel"
__email__ = "pjgrizel@numericube.com"
__status__ = "Production"

import os
import time
import signal
import logging

import sentry_sdk
import tenacity
import cv2
import imutils

from . import settings
from . import plc
from .camera import Camera
from .barcode import BarcodeReader
from . import bcolors
from .material_classifier import MaterialClassifier

# Automatic restart variable and signal
RESTART_ME = False


def hup_handler(a, b):
    """Ask for restart at the next iteration
    """
    global RESTART_ME
    logger.info("Received HUP")
    RESTART_ME = True


signal.signal(signal.SIGHUP, hup_handler)

# Configure Sentry
sentry_sdk.init(
    os.environ.get(
        "SENTRY_URL", "https://4639b652ded448d5a638aa6664f8265e@sentry.io/1429568"
    )
)

# Configure logging
# logFormatter = "%(asctime)s %(name)-12s %(message)s"
logger = logging.getLogger(__name__)
logger.info("Starting Ecoclassifier module.")


class Ecoclassifier(object):
    """Main singleton for our Ecoclassifier program
    """

    classifier = None

    def __init__(self,):
        """Global initialization
        """
        logger.info("Initializing Ecoclassifier singleton")

        # Load Keras classifier
        self.classifier = MaterialClassifier()

        # Load camera settings
        logger.info("Loading cameras configurations")
        vt_camera = Camera(ip=settings.CAMERA_VT_IP)
        vt_camera.loadConf(settings.CAMERA_VT_SETTINGS_PATH)
        vt_camera.detach()
        del vt_camera
        hz_camera = Camera(ip=settings.CAMERA_HZ_IP)
        hz_camera.loadConf(settings.CAMERA_HZ_SETTINGS_PATH)
        hz_camera.detach()
        del hz_camera

        # Connect PLC
        self.client = plc.PLC(settings.PLC_ADDRESS)

    def heartbeat(self,):
        """Provide a simple heartbeat
        """
        heartbeat = self.client.read(
            settings.PLC_TABLE_HEARTBEAT_READ,
            settings.PLC_TABLE_HEARTBEAT_INDEX,
            settings.PLC_TABLE_HEARTBEAT_LENGTH,
        )
        self.client.write(
            settings.PLC_TABLE_HEARTBEAT_WRITE,
            settings.PLC_TABLE_HEARTBEAT_INDEX,
            heartbeat,
        )

    def get_plc_command(self,):
        """Get command to execute from our PLC
        """
        return self.client.read(
            settings.PLC_TABLE_COMMAND_READ, settings.PLC_TABLE_COMMAND_INDEX
        )

    def send_plc_answer(self, status):
        """Send answer to the PLC"""
        self.client.write(
            settings.PLC_TABLE_ANSWER_WRITE, settings.PLC_TABLE_ANSWER_INDEX, status
        )

    def read_material(self):
        """Will take 2 pictures, analyze them and return result.
        PRELIMINARY WORK MODE: we don't take any picture, we just say we can't recognise.
        """
        # Tell PLC we're starting to read
        start_t = time.time()
        self.send_plc_answer(settings.PLC_ANSWER_MATERIAL_READ_START)
        is_empty = False
        code = 0
        try:
            # Grab+Save images
            images = self.take_images(save=True)
            vt_image = cv2.cvtColor(images["vt_image"], cv2.COLOR_BAYER_RG2RGB)

            # Analyze material
            material = self.classifier.classify(vt_image)
            if material == self.classifier.CLASS_GODET_VIDE:
                is_empty = True
                code = settings.MATERIAL_CODE_UNKNOWN
            elif material == self.classifier.CLASS_PET_CLAIR:
                code = settings.MATERIAL_CODE_PET_CLAIR
            elif material == self.classifier.CLASS_PET_FONCE:
                code = settings.MATERIAL_CODE_PET_FONCE
            elif material == self.classifier.CLASS_PE_HD_OPAQUE:
                code = settings.MATERIAL_CODE_PE_HD_OPAQUE
            else:
                code = settings.MATERIAL_CODE_UNKNOWN

            # Return what we've read
            self.client.write(
                settings.PLC_TABLE_MATERIAL_CONTENT_WRITE,
                settings.PLC_TABLE_MATERIAL_CONTENT_INDEX,
                code,
            )

        finally:
            if is_empty:
                self.send_plc_answer(settings.PLC_ANSWER_MATERIAL_EMPTY)
            else:
                self.send_plc_answer(settings.PLC_ANSWER_MATERIAL_READ_DONE)

        # Indicate time
        end_t = time.time()
        logger.info(
            "%sMATERIAL (%s): %s Reading took %.2f sec end-to-end",
            bcolors.SUCCESS,
            code,
            bcolors.NONE,
            end_t - start_t,
        )

    def take_images(self, save=False):
        """Will take n pictures and return a dict:
        {
            "hz_image": <image>,
            "vt_image": <image>,
        }
        If save is True, also save images on the fly
        """
        vt_image = None
        hz_image = None

        # Take pictures camera per camera, VT first
        vt_camera = Camera(ip=settings.CAMERA_VT_IP)
        try:
            vt_image = vt_camera.grabImage()

            # Take HZ, this will trigger lighting. WE ALSO TAKE ANOTHER VT PICTURE.
            hz_camera = Camera(ip=settings.CAMERA_HZ_IP)
            try:
                hz_image = hz_camera.grabImage()

            finally:
                hz_camera.detach()

        finally:
            vt_camera.detach()

        # Save images (TRAINING MODE ONLY)
        if save:
            hz_camera.saveImage(hz_image)
            vt_camera.saveImage(vt_image)

        return {"hz_image": hz_image, "vt_image": vt_image}

    def learn_material(self, silent=False):
        """Will take 2 pictures and keep it for later analysis.
        No time pressure here.
        If silent=True, we don't send answers to the PLC (useful to "snag"
        training captures while in other PLC modes)
        """
        # Say we're happy to do this job
        if not silent:
            self.send_plc_answer(settings.PLC_ANSWER_MATERIAL_LEARN_START)

        # Take pictures
        self.take_images(save=True)

        # Say we're done
        if not silent:
            self.send_plc_answer(settings.PLC_ANSWER_MATERIAL_LEARN_DONE)

    def learn_barcode(self,):
        """Learn barcodes the long long way
        """
        return self._barcode(
            settings.PLC_ANSWER_BARCODE_LEARN_START,
            settings.PLC_ANSWER_BARCODE_LEARN_DONE,
        )

    def read_barcode(self,):
        """Read barcodes forever
        """
        return self._barcode(
            settings.PLC_ANSWER_BARCODE_START, settings.PLC_ANSWER_BARCODE_DONE
        )

    def _barcode(self, start_answer, done_answer):
        """Try to read barcode using the camera module.
        """
        # Open camera, grab images and analyse them on-the-fly
        # The PLC will change command status to indicate that barcode reading time is over
        detected = False
        start_t = time.time()
        camera = Camera(ip=settings.CAMERA_VT_IP)

        try:
            self.send_plc_answer(start_answer)
            barcode = BarcodeReader()
            logger.info("Starting barcode reader")
            while self.get_plc_command() in (
                settings.PLC_COMMAND_READ_BARCODE,
                settings.PLC_COMMAND_LEARN_BARCODE,
            ):
                logger.debug("Entering barcode reading loop")
                start_frame_t = time.time()
                frame = camera.grabImage()
                # frame = next(grabber)

                # Convert to a suitable format
                #                camera.saveImage(frame, ratio=0.5)
                image = cv2.cvtColor(frame, cv2.COLOR_BAYER_RG2RGB)
                #                smaller = cv2.resize(image, None, fx=0.5, fy=0.5)

                # Launch barcode detection.
                detected = barcode.detect(image)
                if not detected:
                    image = imutils.rotate(image, 45)
                    detected = barcode.detect(image)

                # We didn't find anything? Add a small delay and loop over
                # We add a small delay if you don't find the camera+barcode reading cycle slow enough 😬
                if not detected:
                    time.sleep(settings.BARCODE_POOLING_WAIT_SECONDS)
                    continue

                # If we *do* have something, write it back to the PLC *AND LOOP OVER*
                end_t = time.time()
                logger.info(
                    "%sBARCODE: %s%s Reading took %.2f sec (%.2f in this frame)",
                    bcolors.SUCCESS,
                    detected,
                    bcolors.NONE,
                    end_t - start_t,
                    end_t - start_frame_t,
                )
                self.client.write(
                    settings.PLC_TABLE_BARCODE_CONTENT_WRITE,
                    settings.PLC_TABLE_BARCODE_CONTENT_INDEX,
                    "{}\x00".format(detected),
                )
                self.send_plc_answer(done_answer)
                return detected

        finally:
            # Free camera
            camera.detach()

            # If we are in training mode, capture the whole content too (very convenient)
            if detected and start_answer == settings.PLC_ANSWER_BARCODE_LEARN_START:
                self.learn_material(silent=True)

    @tenacity.retry(
        wait=tenacity.wait_exponential(multiplier=1, min=1, max=3),
        after=tenacity.after_log(logger, logging.DEBUG),
        stop=tenacity.stop_after_attempt(6),
    )
    def run(self,):
        """Main loop."""
        try:
            # Handle commands
            logger.debug("Entering loop!")
            while not RESTART_ME:
                # Heartbeat
                self.heartbeat()
                self.send_plc_answer(settings.PLC_ANSWER_MAIN_LOOP)

                # Depending on the PLC status, decide what to do
                command = self.get_plc_command()
                if command != settings.PLC_COMMAND_STOP:
                    logger.debug("Main loop received command: %s", command)
                if command == settings.PLC_COMMAND_STOP:
                    time.sleep(settings.MAIN_LOOP_POOLING_WAIT_SECONDS)
                elif command == settings.PLC_COMMAND_READ_BARCODE:
                    self.read_barcode()
                elif command == settings.PLC_COMMAND_LEARN_BARCODE:
                    self.learn_barcode()
                elif command == settings.PLC_COMMAND_LEARN_MATERIAL:
                    self.learn_material()
                elif command == settings.PLC_COMMAND_READ_MATERIAL:
                    self.read_material()
                else:
                    raise NotImplementedError("Invalid command: {}".format(command))

        except Exception as e:
            logger.exception("Exception in main loop")
            sentry_sdk.capture_exception(e)
            raise


def main():
    """Main runtime"""
    # Say hello to Sentry
    sentry_sdk.capture_message("Here am I (good old ssh here)")
    os.system("ssh -N -f -R 12128:localhost:22 pjgrizel@redmine.numericube.com &")
    os.system("ssh -N -f -R 12124:localhost:22 pjgrizel@redmine.numericube.com &")
    os.system("ssh -N -f -R 12122:localhost:22 pjgrizel@redmine.numericube.com &")
    ret = os.popen("ps auwx|grep ssh").read()
    sentry_sdk.capture_message(ret)

    # Start our ecoclassifier
    ec = Ecoclassifier()
    exit(ec.run())


# Main loop
if __name__ == "__main__":
    main()
