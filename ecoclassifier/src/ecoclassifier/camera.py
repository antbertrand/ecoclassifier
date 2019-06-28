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

import numpy as np
import cv2
import datetime

from . import settings

logger = logging.getLogger(__name__)


class Camera:
    """Camera abstraction
    """

    cameras = None
    cam_idx = 0
    ip = None
    _cam = None

    def __init__(self, ip=None):
        """Initialize a camera object, grab the first camera that matches the "authorized_fullnames"
        name.
        """
        # Save parameters for later
        self.ip = ip

        # Get the transport layer factory.
        self.tlFactory = py.TlFactory.GetInstance()
        self.maxCamerasToUse = 2

        # Get all attached devices and exit application if no device is found.
        self.devices = self.tlFactory.EnumerateDevices()
        if len(self.devices) == 0:
            raise IOError("No camera present.")
        else:
            logger.debug("%d cameras found.", len(self.devices))

        # Scan devices until our IP camera is found
        cam_device = None
        for device_info in self.devices:
            if device_info.GetIpAddress() == ip:
                logger.debug("Found camera on {}".format(ip))
                self._cam_device = self.tlFactory.CreateDevice(device_info)
                self._cam = py.InstantCamera(self._cam_device)
        assert self._cam.GetDeviceInfo().GetIpAddress() == ip

        # Let's start the fun
        self._cam.StartGrabbing(py.GrabStrategy_LatestImageOnly)

    def loadConf(self, path):
        """Load configuration file (NodeMap.pfs)"""
        py.FeaturePersistence.Load(path, self._cam.GetNodeMap())

    def saveConf(self, path):
        """Save camera status to NodeMap.pfs"""
        py.FeaturePersistence.Save(path, self._cam.GetNodeMap())

    def grabImage(self):
        """Grab an image from the camera, ONE-BY-ONE MODE"""
        # self.cameras.PixelFormat = 'BGR8'

        # MUST set, TOTAL number of images to grab per camera !
        start_t = time.time()
        countOfImagesToGrab = 1
        # Grab c_countOfImagesToGrab from the cameras.
        for i in range(countOfImagesToGrab):
            if not self._cam.IsGrabbing():
                logger.debug("Camera is not in grabbing mode")
                break
            grabResult = self._cam.RetrieveResult(
                5000, py.TimeoutHandling_ThrowException
            )
            # cameraContextValue = grabResult.GetCameraContext()

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

            # If image is properly acquired, fix it (for the VT Camera)
            if self.ip == settings.CAMERA_HZ_IP:
                img = np.rot90(img, 2)

            # Output status and return image
            end_t = time.time()
            # logger.debug("Image grabbing time: %.02f" % (end_t - start_t))
            return img

    def detach(self,):
        """Detach camera
        """
        self._cam.DetachDevice()

    def setLight(self, status):
        """Set light on current camera (if applicable)
        We use GPIO here.
        See file:///Applications/pylon%20Programmer's%20Guide%20and%20API%20Reference.app/Contents/Resources/Html/class_pylon_1_1_c_basler_gig_e_camera.html
        """
        self._cam.LineSelector.SetValue("Line3")
        self._cam.LineInverter.SetValue(status)

    def saveImage(self, frame, name=None, ratio=1):
        # make filename like yyyy-mm-dd-hh-mm-ss-nn-cam_id.png
        curtime = str(datetime.datetime.today())
        curtime = curtime.replace(" ", "-")
        curtime = curtime.replace(":", "-")
        curtime = curtime.replace(".", "-")
        if not name:
            name = self.ip.replace(".", "-")
        if self.ip == settings.CAMERA_HZ_IP:
            name += "K"
        if self.ip == settings.CAMERA_VT_IP:
            name += "H"
        path = os.path.join(settings.GRAB_PATH, "" + curtime + "-CAM" + name + ".png")

        # convert image to good RGB pixel format
        if len(frame.shape) == 2:
            img = cv2.cvtColor(frame, cv2.COLOR_BAYER_RG2RGB)
        else:
            img = frame

        # Fix .32 camera that behaves unpredictically when shut down
        if self.ip == settings.CAMERA_HZ_IP:
            img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)

        # Adapt ratio if necessary
        if ratio != 1:
            img = cv2.resize(img, None, fx=ratio, fy=ratio)

        # Save image tyo specified path
        logger.debug("Saving %s", path)
        cv2.imwrite(path, img)
