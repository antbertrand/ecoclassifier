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
import logging

import sentry_sdk
import tenacity
import cv2

# pylint: disable=F403
from . import settings
from . import plc
from .camera import Camera
from .barcode import BarcodeReader
from . import bcolors

# Configure Sentry
sentry_sdk.init(
    os.environ.get(
        "SENTRY_URL", "https://4639b652ded448d5a638aa6664f8265e@sentry.io/1429568"
    )
)

# Configure logging
# logFormatter = "%(asctime)s %(name)-12s %(message)s"
logFormatter = "[%(asctime)s] p%(process)-8s %(levelname)-8s {%(pathname)s:%(lineno)d} - %(message)s"
logging.basicConfig(format=logFormatter, level=logging.DEBUG)
logger = logging.getLogger(__name__)
logger.info("Starting Ecoclassifier module.")


class Ecoclassifier(object):
    """Main singleton for our Ecoclassifier program
    """

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
        start_t = time.time()
        camera = Camera(ip=settings.CAMERA_VT_IP, continuous=True)
        grabber = camera.continuousGrab()
        try:
            self.send_plc_answer(start_answer)
            barcode = BarcodeReader()
            logger.info("Starting barcode reader")
            while self.get_plc_command() in (
                settings.PLC_COMMAND_READ_BARCODE,
                settings.PLC_COMMAND_LEARN_BARCODE,
            ):
                logger.debug("")
                start_frame_t = time.time()
                logger.debug("")
                #frame = camera.grabImage()
                frame = next(grabber)
                logger.debug("")

                # Convert to a suitable format
                camera.saveImage(frame, ratio=0.5)
                logger.debug("")
                image = cv2.cvtColor(frame, cv2.COLOR_BAYER_RG2RGB)
                logger.debug("")
                smaller = cv2.resize(image, None, fx=0.5, fy=0.5)
                logger.debug("")

                # Launch barcode detection. If we *do* have something, write it back to the PLC
                logger.debug("")
                detected = barcode.detect(smaller)
                logger.debug("")
                if detected:
                    logger.debug("")
                    end_t = time.time()
                    logger.info(
                        "%sEAN13: %s%s Reading took %.2f sec (%.2f in this frame)" % (bcolors.SUCCESS, detected, bcolors.NONE, end_t - start_t, end_t - start_frame_t)
                    )
                    self.client.write(
                        settings.PLC_TABLE_BARCODE_CONTENT_WRITE,
                        settings.PLC_TABLE_BARCODE_CONTENT_INDEX,
                        detected,
                    )
                    self.send_plc_answer(done_answer)
                    return detected

                # Add a small delay if you don't find the camera+barcode reading cycle slow enough 😬
                time.sleep(settings.BARCODE_POOLING_WAIT_SECONDS)

        finally:
            camera.detach()

    @tenacity.retry(
        wait=tenacity.wait_exponential(multiplier=1, min=2, max=600),
        after=tenacity.after_log(logger, logging.DEBUG),
    )
    def run(self,):
        """Main loop"""
        try:
            # Connect PLC
            self.client = plc.PLC(settings.PLC_ADDRESS)

            while True:
                # Heartbeat
                logger.debug("Entering loop!")
                self.heartbeat()
                self.send_plc_answer(settings.PLC_ANSWER_MAIN_LOOP)

                # Depending on the PLC status, decide what to do
                command = self.get_plc_command()
                if command == settings.PLC_COMMAND_STOP:
                    self.read_barcode()
                    time.sleep(settings.MAIN_LOOP_POOLING_WAIT_SECONDS)
                elif command == settings.PLC_COMMAND_READ_BARCODE:
                    self.read_barcode()
                elif command == settings.PLC_COMMAND_LEARN_BARCODE:
                    self.learn_barcode()
                else:
                    raise NotImplementedError("Invalid command: {}".format(command))

        except Exception as e:
            logger.exception("Exception in main loop")
            sentry_sdk.capture_exception(e)
            raise


def main():
    """Main runtime"""
    ec = Ecoclassifier()
    exit(ec.run())


# Main loop
if __name__ == "__main__":
    main()
