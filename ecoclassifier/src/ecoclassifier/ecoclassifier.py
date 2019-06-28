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
import glob
import shutil
import datetime

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
    vt_camera = None
    hz_camera = None

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

    def is_door_opened(self,):
        """Return True if door is closed.
        """
        return (
            self.client.read(
                settings.PLC_TABLE_COMMAND_READ, settings.PLC_TABLE_DOOR_INDEX
            )
            == settings.PLC_DOOR_OPENED
        )

    def get_material(self, vt_image, hz_image):
        """Read current material (by taking pictures) and return it.
        Return None for godet vide
        """
        # Grab+Save images
        start_t = time.time()
        converted = cv2.cvtColor(vt_image, cv2.COLOR_BAYER_RG2RGB)

        # Analyze material
        material = self.classifier.classify(converted)
        if material == self.classifier.CLASS_GODET_VIDE:
            code = None
        elif material == self.classifier.CLASS_PET_CLAIR:
            code = settings.MATERIAL_CODE_PET_CLAIR
        elif material == self.classifier.CLASS_PET_FONCE:
            code = settings.MATERIAL_CODE_PET_FONCE
        elif material == self.classifier.CLASS_PE_HD_OPAQUE:
            code = settings.MATERIAL_CODE_PE_HD_OPAQUE
        else:
            code = settings.MATERIAL_CODE_UNKNOWN

        # Indicate time
        end_t = time.time()
        logger.info(
            "%sMATERIAL (%s): %s Reading took %.2f sec end-to-end",
            bcolors.SUCCESS,
            code,
            bcolors.NONE,
            end_t - start_t,
        )

        # Return material code
        return code

    #
    # def read_material(self, code=None):
    #     """Will take 2 pictures, analyze them and return result.
    #     If code is set, we don't perform analysis, we just process it.
    #     If it's not set, we call get_material() to take pictures and read it.
    #     """
    #     # Tell PLC we're starting to read
    #     self.send_plc_answer(settings.PLC_ANSWER_MATERIAL_READ_START)
    #     is_empty = False
    #     try:
    #         if code is None:
    #             code = self.get_material()
    #         if code is None:
    #             is_empty = True
    #             code = settings.MATERIAL_CODE_UNKNOWN
    #
    #         # Return what we've read
    #         self.client.write(
    #             settings.PLC_TABLE_MATERIAL_CONTENT_WRITE,
    #             settings.PLC_TABLE_MATERIAL_CONTENT_INDEX,
    #             code,
    #         )
    #
    #     finally:
    #         if is_empty:
    #             self.send_plc_answer(settings.PLC_ANSWER_MATERIAL_EMPTY)
    #         else:
    #             self.send_plc_answer(settings.PLC_ANSWER_MATERIAL_READ_DONE)

    # def take_images(self, save=False):
    #     """Will take n pictures and return a dict:
    #     {
    #         "hz_image": <image>,
    #         "vt_image": <image>,
    #     }
    #     If save is True, also save images on the fly
    #     """
    #     start_t = time.time()
    #     vt_image = None
    #     hz_image = None
    #
    #     # Take pictures camera per camera, VT first
    #     # vt_camera = Camera(ip=settings.CAMERA_VT_IP)
    #     try:
    #         vt_image = self.vt_camera.grabImage()
    #
    #         # Take HZ, this will trigger lighting. WE ALSO TAKE ANOTHER VT PICTURE.
    #         # hz_camera = Camera(ip=settings.CAMERA_HZ_IP)
    #         try:
    #             hz_image = self.hz_camera.grabImage()
    #
    #         finally:
    #             pass
    #             # hz_camera.detach()
    #
    #     finally:
    #         pass
    #         # vt_camera.detach()
    #
    #     # Save images (TRAINING MODE ONLY)
    #     start_save_t = time.time()
    #     if save:
    #         self.hz_camera.saveImage(hz_image)
    #         self.vt_camera.saveImage(vt_image)
    #
    #     # Performance monitoring
    #     end_t = time.time()
    #     logger.info(
    #         "%sIMAGE:%s Capture took %.2f sec (%.2f to save on disk)",
    #         bcolors.SUCCESS,
    #         bcolors.NONE,
    #         end_t - start_t,
    #         end_t - start_save_t,
    #     )
    #
    #     return {"hz_image": hz_image, "vt_image": vt_image}

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
        vt_image, hz_image = self.grab_images(self.is_door_opened())
        self.save_images(vt_image, hz_image)

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
                frame = self.grab_images(self.is_door_opened())[0]

                # Convert to a suitable format
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
            # If we are in training mode, capture the whole content too (very convenient)
            if detected and start_answer == settings.PLC_ANSWER_BARCODE_LEARN_START:
                self.learn_material(silent=True)

    def grab_images(self, door_is_opened=True):
        """Return a (vt_array, hz_array) image tuple.
        If front door is open, do NOT take a picture with HZ camera.
        """
        vt_image = None
        hz_image = None

        # Take pictures camera per camera, VT first
        vt_camera = Camera(ip=settings.CAMERA_VT_IP)
        try:
            vt_image = vt_camera.grabImage()

            # Take HZ, this will trigger lighting.
            if not door_is_opened:
                hz_camera = Camera(ip=settings.CAMERA_HZ_IP)
                try:
                    hz_image = hz_camera.grabImage()

                finally:
                    hz_camera.detach()

        finally:
            vt_camera.detach()

        return (vt_image, hz_image)

    def save_images(self, vt_image, hz_image, ratio=1):
        """Save images on the fly"""
        for ip, frame in (
            (settings.CAMERA_VT_IP, vt_image),
            (settings.CAMERA_HZ_IP, hz_image),
        ):
            # make filename like yyyy-mm-dd-hh-mm-ss-nn-cam_id.png
            curtime = str(datetime.datetime.today())
            curtime = curtime.replace(" ", "-")
            curtime = curtime.replace(":", "-")
            curtime = curtime.replace(".", "-")
            name = ip.replace(".", "-")
            if ip == settings.CAMERA_HZ_IP:
                name += "K"
            elif ip == settings.CAMERA_VT_IP:
                name += "H"
            path = os.path.join(
                settings.GRAB_PATH, "" + curtime + "-CAM" + name + ".png"
            )

            # convert image to good RGB pixel format
            if len(frame.shape) == 2:
                img = cv2.cvtColor(frame, cv2.COLOR_BAYER_RG2RGB)
            else:
                img = frame

            # Fix .32 camera that behaves unpredictically when shut down
            if ip == settings.CAMERA_HZ_IP:
                img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)

            # Adapt ratio if necessary
            if ratio != 1:
                img = cv2.resize(img, None, fx=ratio, fy=ratio)

            # Save image tyo specified path
            logger.debug("Saving %s", path)
            cv2.imwrite(path, img)

    @tenacity.retry(
        wait=tenacity.wait_exponential(multiplier=1, min=1, max=3),
        after=tenacity.after_log(logger, logging.DEBUG),
        stop=tenacity.stop_after_attempt(6),
    )
    def run(self,):
        """Main loop."""
        try:
            # Door state and flip-flop memory.
            # If door is already closed, take a picture just in case.
            door_was_open = self.is_door_opened()
            current_material = settings.MATERIAL_CODE_UNKNOWN
            if not self.is_door_opened():
                vt_image, hz_image = self.grab_images(False)
                current_material = self.get_material(vt_image, hz_image)

            # Main program loop
            logger.debug("Entering loop!")
            while not RESTART_ME:
                # Heartbeat
                self.heartbeat()
                self.send_plc_answer(settings.PLC_ANSWER_MAIN_LOOP)

                # The flip-flop door: did it close? If so, we read material right now.
                if self.is_door_opened():
                    door_was_open = True
                elif door_was_open:
                    door_was_open = False
                    vt_image, hz_image = self.grab_images(self.is_door_opened())
                    current_material = self.get_material(vt_image, hz_image)

                # Depending on the PLC status, decide what to do
                command = self.get_plc_command()
                if command != settings.PLC_COMMAND_STOP:
                    logger.debug("Main loop received command: %s", command)

                # Depending on the PLC status, decide what to do
                if command == settings.PLC_COMMAND_STOP:
                    time.sleep(settings.MAIN_LOOP_POOLING_WAIT_SECONDS)

                # Barcode management
                elif command == settings.PLC_COMMAND_READ_BARCODE:
                    self.read_barcode()
                elif command == settings.PLC_COMMAND_LEARN_BARCODE:
                    self.learn_barcode()

                elif command == settings.PLC_COMMAND_LEARN_MATERIAL:
                    self.learn_material()

                # Convert and return material, THEN record images
                elif command == settings.PLC_COMMAND_READ_MATERIAL:
                    self.send_plc_answer(settings.PLC_ANSWER_MATERIAL_READ_START)
                    logger.debug("Sending material code to PLC: %s", current_material)
                    if current_material is None:
                        self.client.write(
                            settings.PLC_TABLE_MATERIAL_CONTENT_WRITE,
                            settings.PLC_TABLE_MATERIAL_CONTENT_INDEX,
                            settings.MATERIAL_CODE_UNKNOWN,
                        )
                        self.send_plc_answer(settings.PLC_ANSWER_MATERIAL_EMPTY)
                    else:
                        self.client.write(
                            settings.PLC_TABLE_MATERIAL_CONTENT_WRITE,
                            settings.PLC_TABLE_MATERIAL_CONTENT_INDEX,
                            current_material,
                        )
                        self.send_plc_answer(settings.PLC_ANSWER_MATERIAL_READ_DONE)

                    # Save images
                    self.save_images(vt_image, hz_image)
                else:
                    raise NotImplementedError("Invalid command: {}".format(command))

        except Exception as e:
            logger.exception("Exception in main loop")
            sentry_sdk.capture_exception(e)
            raise


def main():
    """Main runtime"""
    # Start our ecoclassifier
    ec = Ecoclassifier()
    exit(ec.run())


# Main loop
if __name__ == "__main__":
    main()
