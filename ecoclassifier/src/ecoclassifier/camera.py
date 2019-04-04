#!/usr/bin/env python
# encoding: utf-8
"""
camera.py

Created by Pierre-Julien Grizel et al.
Copyright (c) 2016 NumeriCube. All rights reserved.

Camera management, the way it's meant to be.
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
import pypylon.pylon as py

# import numpy as np
import cv2
import datetime

from . import settings

logFormatter = "[%(asctime)s] p%(process)-8s %(levelname)-8s {%(pathname)s:%(lineno)d} - %(message)s"
logging.basicConfig(format=logFormatter, level=logging.DEBUG)
logger = logging.getLogger(__name__)


class Camera:
    cameras = None
    cam_idx = 0

    def __init__(self, ip=None, continuous=False):
        """Initialize a camera object, grab the first camera that matches the "authorized_fullnames"
        name.
        """
        # Get the transport layer factory.
        self.tlFactory = py.TlFactory.GetInstance()

        self.maxCamerasToUse = 2
        # Get all attached devices and exit application if no device is found.
        self.devices = self.tlFactory.EnumerateDevices()
        if len(self.devices) == 0:
            raise pylon.RUNTIME_EXCEPTION("No camera present.")
        else:
            logger.debug("%d cameras found.", len(self.devices))

        # Create an array of instant cameras for the found devices and avoid exceeding a maximum number of devices.
        self.cameras = py.InstantCameraArray(
            min(len(self.devices), self.maxCamerasToUse)
        )

        # Create and attach all Pylon Devices.
        for i, cam in enumerate(self.cameras):
            cam.Attach(self.tlFactory.CreateDevice(self.devices[i]))
            if ip and cam.GetDeviceInfo().GetIpAddress() == ip:
                logger.debug(
                    "Using %s on %s",
                    cam.GetDeviceInfo().GetFriendlyName(),
                    cam.GetDeviceInfo().GetIpAddress(),
                )
                cam_idx = i
                break
            else:
                logger.debug(
                    "Ignoring %s on %s",
                    cam.GetDeviceInfo().GetFriendlyName(),
                    cam.GetDeviceInfo().GetIpAddress(),
                )
            print("Using device ", cam.GetDeviceInfo().GetModelName())

        # Let's start the fun
        if continuous:
            self.cameras[self.cam_idx].StartGrabbingMax(100)
        else:
            # self.cameras[self.cam_idx].StartGrabbing(py.GrabStrategy_LatestImages)
            self.cameras[self.cam_idx].StartGrabbing(py.GrabStrategy_LatestImageOnly)
        # self.cameras.PixelFormat = 'RGB8'

    def continuousGrab(self,):
        """Continuously grab images
        """
        camera = self.cameras[self.cam_idx]
        while camera.IsGrabbing():
            grabResult = camera.RetrieveResult(5000, py.TimeoutHandling_ThrowException)

            # Image grabbed successfully?
            if grabResult.GrabSucceeded():
                # Access the image data.
                # print("SizeX: ", grabResult.Width)
                # print("SizeY: ", grabResult.Height)
                img = grabResult.Array
                grabResult.Release()
                yield img
                # print("Gray value of first pixel: ", img[0, 0])
            else:
                logger.debug(
                    "%s / %s" % (grabResult.ErrorCode, grabResult.ErrorDescription)
                )

    def loadConf(self):
        """Load configuration file (NodeMap.pfs)"""
        py.FeaturePersistence.Load(self.conf, self.instant_camera.GetNodeMap())
        return "Config Loaded"

    def saveConf(self):
        """Save camera status to NodeMap.pfs"""
        py.FeaturePersistence.Save(self.conf, self.instant_camera.GetNodeMap())
        return "Config Saved"

    def ROI(self, width, height, offsetX, offsetY):
        """ROI is like a square(define by width and height)
        #moving by offset settings (define by OffsetX and OffsetY)
        #For Auto - Brightness/WithBalance/Gain adjust ON THE ROI
        #settings GainAuto and BalanceWhitAuto MUST be set in Continuous mode
        """
        Camera.setAutoGain(self)
        Camera.setAutoWhiteBalance(self)

        for cam in self.cameras:

            # Define correct target AutoTargetBrightness.
            # It's the target goal for image settings quality.
            # Must be set between [0.19608 to 0.80392]
            # cam.AutoTargetBrightness.SetValue(AutoTargetBrightnessValue)

            # select the ROI1. You can use two ROI, (ROI1 and ROI2)
            cam.AutoFunctionROISelector.SetValue("ROI1")

            # ROI is like a square(define by width and height)
            # moving by offset settings (define by OffsetX and OffsetY)

            # Set the square Width
            cam.AutoFunctionROIWidth.SetValue(width)
            # Set the square Height
            cam.AutoFunctionROIHeight.SetValue(height)
            # Set the OffsetX
            cam.AutoFunctionROIOffsetX.SetValue(offsetX)
            # Set the Offsety
            cam.AutoFunctionROIOffsetY.SetValue(offsetY)

            # Set auto adjust Brightness and WhiteBalance in Continuous Mode, for the ROI's
            cam.AutoFunctionROIUseBrightness.SetValue(1)
            cam.AutoFunctionROIUseWhiteBalance.SetValue(1)

    def setAutoExposure(self):
        """To set Auto Exposure in Continuous Mode
        """
        for cam in self.cameras:
            cam.ExposureAuto.SetValue("Continuous")

    def setAutoGain(self):
        """To set Auto Gain in Continuous Mode
        """
        for cam in self.cameras:
            cam.GainAuto.SetValue("Continuous")

    def setAutoWhiteBalance(self):
        """To set AutoWhiteBalance in Continuous Mode
        """
        for cam in self.cameras:
            cam.BalanceWhiteAuto.SetValue("Continuous")

    def grabImage(self):
        """Grab an image from the camera, ONE-BY-ONE MODE"""
        # self.cameras.PixelFormat = 'BGR8'

        # MUST set, TOTAL number of images to grab per camera !
        start_t = time.time()
        countOfImagesToGrab = 1
        # Grab c_countOfImagesToGrab from the cameras.
        for i in range(countOfImagesToGrab):
            if not self.cameras[self.cam_idx].IsGrabbing():
                logger.debug("Camera is not in grabbing mode")
                break
            cam = self.cameras[self.cam_idx]
            grabResult = cam.RetrieveResult(5000, py.TimeoutHandling_ThrowException)
            cameraContextValue = grabResult.GetCameraContext()

            # Print the index and the model name of the camera.
            # print("Camera ", cameraContextValue, ": ", self.cameras[cameraContextValue].GetDeviceInfo().GetModelName())

            # Now, the image data can be processed.
            # print("GrabSucceeded: ", grabResult.GrabSucceeded())
            # print("SizeX: ", grabResult.GetWidth())
            # print("SizeY: ", grabResult.GetHeight())
            img = grabResult.GetArray()
            grabResult.Release()
            # print("Gray value of first pixel: ", img[0, 0])
            # img = cv2.cvtColor(img, cv2.COLOR_BAYER_RG2RGB)

            # Output status and return image
            end_t = time.time()
            logger.debug("Image grabbing time: %.02f" % (end_t - start_t))
            return img

    def detach(self,):
        """Detach camera
        """
        for cam in self.cameras:
            det = cam.DetachDevice()

    def saveImage(self, frame, camera_id="0", ratio=1):
        # make filename like yyyy-mm-dd-hh-mm-ss-nn-cam_id.png
        curtime = str(datetime.datetime.today())
        curtime = curtime.replace(" ", "-")
        curtime = curtime.replace(":", "-")
        curtime = curtime.replace(".", "-")
        path = os.path.join(
            settings.GRAB_PATH, "" + curtime + "-CAM" + str(camera_id) + ".png"
        )

        # convert image to good RGB pixel format
        if len(frame.shape) == 2:
            img = cv2.cvtColor(frame, cv2.COLOR_BAYER_RG2RGB)
        else:
            img = frame

        # Adapt ratio if necessary
        if ratio != 1:
            img = cv2.resize(img, None, fx=ratio, fy=ratio)

        # Save image tyo specified path
        logger.debug("Saving %s", path)
        cv2.imwrite(path, img)
