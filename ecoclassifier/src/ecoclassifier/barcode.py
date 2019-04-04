#!/usr/bin/env python
# encoding: utf-8
"""
barcode.py

Created by Pierre-Julien Grizel et al.
Copyright (c) 2016 NumeriCube. All rights reserved.

The barcode reader
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

import time
import logging

from pyzbar import pyzbar

# Logging configuration
logFormatter = "[%(asctime)s] p%(process)-8s %(levelname)-8s {%(pathname)s:%(lineno)d} - %(message)s"
logging.basicConfig(format=logFormatter, level=logging.DEBUG)
logger = logging.getLogger(__name__)


class BarcodeReader(object):
    """Generic barcode reader
    """

    barcode_types = ()

    def __init__(self, barcode_types=(pyzbar.ZBarSymbol.EAN13,)):
        """Initial configuration
        """
        self.barcode_types = barcode_types

    def detect(self, image):
        """Detect a barcode on an image read from the camera.
        """
        # grab Image from camera
        # image = cam.grabImage()
        # load the input image
        # image = cv2.imread(args["image"])

        # find the barcodes in the image and decode each of the barcodes
        logger.debug("Trying to detect barcode (image size=%s)", image.shape)
        start = time.time()
        barcodes = pyzbar.decode(image, self.barcode_types)
        end = time.time()

        # loop over the detected barcodes
        for barcode in barcodes:
            # extract the bounding box location of the barcode and draw the
            # bounding box surrounding the barcode on the image
            # (x, y, w, h) = barcode.rect
            # cv2.rectangle(image, (x, y), (x + w, y + h), (0, 0, 255), 2)

            # the barcode data is a bytes object so if we want to draw it on
            # our output image we need to convert it to a string first
            barcode_data = barcode.data.decode("utf-8")
            barcode_type = barcode.type

            # draw the barcode data and barcode type on the image
            # text = "{} ({})".type(barcodeData, barcodeType)
            # cv2.putText(image, text, (x, y - 10), cv2.FONT_HERSHEY_SIMPLEX,
            # 	0.5, (0, 0, 255), 2)

            # print the barcode type and data to the terminal
            logger.debug(
                "Found %s barcode: %s in %.2f seconds",
                barcode_type,
                barcode_data,
                (end - start),
            )
            if not barcode_type in [b.name for b in self.barcode_types]:
                continue

            # Return it
            return barcode_data

        # No barcode found? Return None
        return None
