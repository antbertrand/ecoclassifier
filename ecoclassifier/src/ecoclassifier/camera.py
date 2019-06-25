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

# Initialize cameras
# devices = None
# cameras = None
# tlFactory = py.TlFactory.GetInstance()
# devices = tlFactory.EnumerateDevices()
# # cameras = py.InstantCameraArray(len(devices))
# for i, cam in enumerate(cameras):
#     cam.Attach(tlFactory.CreateDevice(devices[i]))
#     logger.debug("Using device %s", cam.GetDeviceInfo().GetIpAddress())
# cameras.StartGrabbing(py.GrabStrategy_LatestImageOnly)

from imageeventprinter import ImageEventPrinter
from .material_classifier import MaterialClassifier

#
# class ImageEventHandler(py.ImageEventHandler):
#     """Handle grabbing events
#     """
#
#     classifier = MaterialClassifier()
#
#     def OnImageGrabbed(self, camera, grabResult):
#         """Capture image, store result
#         """
#         global HZ_IMAGE
#         global VT_IMAGE
#         print("OnImageGrabbed event for device ", camera.GetDeviceInfo().GetModelName())
#
#         # Image grabbed successfully?
#         if grabResult.GrabSucceeded():
#             print("SizeX: ", grabResult.GetWidth())
#             print("SizeY: ", grabResult.GetHeight())
#             img = grabResult.GetArray()
#             print("Gray values of first row: ", img[0])
#
#             # Mark images as acquired
#             if camera.GetDeviceInfo().GetIpAddress() == settings.CAMERA_VT_IP:
#                 print("Perform material classification")
#                 # classifier = MaterialClassifier()
#                 material = self.classifier.classify(img)
#                 print("DETECTED MATERIAL: ", material)
#                 VT_IMAGE = True
#             else:
#                 HZ_IMAGE = True
#         else:
#             print(
#                 "Error: ", grabResult.GetErrorCode(), grabResult.GetErrorDescription()
#             )
#


class Cameras:
    """Camera pair abstraction.
    Taken from https://github.com/basler/pypylon/issues/83
    """

    def __init__(self):
        pylon = py
        tlFactory = pylon.TlFactory.GetInstance()

        # Get all attached devices and exit application if no device is found.
        devices = tlFactory.EnumerateDevices()
        if len(devices) == 0:
            raise pylon.RUNTIME_EXCEPTION("No camera present.")

        # Create an array of instant cameras for the found devices and avoid exceeding a maximum number of devices.
        self.cameras = pylon.InstantCameraArray(min(len(devices), 2))

        # Create and attach all Pylon Devices.
        for i, cam in enumerate(self.cameras):
            cam.Attach(tlFactory.CreateDevice(devices[i]))
            cam.RegisterConfiguration(
                pylon.ConfigurationEventHandler(),
                pylon.RegistrationMode_ReplaceAll,
                pylon.Cleanup_Delete,
            )
            # For demonstration purposes only, add a sample configuration event handler to print out information
            # about camera use.t
            # cam.RegisterConfiguration(
            #     ConfigurationEventPrinter(),
            #     pylon.RegistrationMode_Append,
            #     pylon.Cleanup_Delete,
            # )
            # The image event printer serves as sample image processing.
            # When using the grab loop thread provided by the Instant Camera object, an image event handler processing the grab
            # results must be created and registered.
            # cam.RegisterImageEventHandler(
            #     ImageEventHandler(), pylon.RegistrationMode_Append, pylon.Cleanup_Delete
            # )

        # Start the grabbing using the grab loop thread, by setting the grabLoopType parameter
        # to GrabLoop_ProvidedByInstantCamera. The grab results are delivered to the image event handlers.
        # The GrabStrategy_OneByOne default grab strategy is used.
        self.cameras.StartGrabbing(
            py.GrabStrategy_LatestImageOnly  # pylon.GrabLoop_ProvidedByInstantCamera
        )
        self.vt_camera = self.cameras[0]
        self.hz_camera = self.cameras[1]

    def grab_images(self, door_open=True):
        """Grab images from the camera, ONE-BY-ONE MODE
        Return (VT, HZ)"""
        # MUST set, TOTAL number of images to grab per camera !
        pylon = py
        start_t = time.time()

        # Light on
        if not door_open:
            self.hz_camera.LineSelector.SetValue("Line3")
            self.hz_camera.LineInverter.SetValue(True)

        # Grab picture (VT camera, with our without light depending on condition)
        if self.vt_camera.WaitForFrameTriggerReady(
            100, pylon.TimeoutHandling_ThrowException
        ):
            self.vt_camera.ExecuteSoftwareTrigger()

        # Turn the light off
        if not door_open:
            self.hz_camera.LineSelector.SetValue("Line3")
            self.hz_camera.LineInverter.SetValue(False)

        if not door_open and self.hz_camera.WaitForFrameTriggerReady(
            100, pylon.TimeoutHandling_ThrowException
        ):
            self.hz_camera.ExecuteSoftwareTrigger()

        # Actually grab images.
        # If door is open, only grab the VT camera
        grab1 = self.vt_camera.RetrieveResult(5000)
        r1 = grab1.GetArray()
        grab1.Release()
        if not door_open:
            grab2 = self.hz_camera.RetrieveResult(5000)
            r2 = grab2.GetArray()
            r2 = np.rot90(r2, 2)
            grab2.Release()
        else:
            r2 = None

        # Output status and return image
        end_t = time.time()
        logger.debug("Image grabbing time: %.02f", (end_t - start_t))
        return r1, r2

    def save_images(self, vt_image, hz_image, name=None, ratio=1):
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
            if not name:
                name = self.ip.replace(".", "-")
            if ip == settings.CAMERA_HZ_IP:
                name += "K"
            if ip == settings.CAMERA_VT_IP:
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


class Camera:
    """Camera abstraction
    """

    # cameras = None
    cam_idx = 0
    ip = None
    # _cam = None

    def __init__(self, ip):
        """Initialize a camera object, grab the first camera that matches the "authorized_fullnames"
        name.
        """
        if ip == settings.CAMERA_VT_IP:
            cam_idx = 0
        else:
            cam_idx = 1

        # Save parameters for later
        self.ip = ip

        # Get the transport layer factory.
        # self.tlFactory = py.TlFactory.GetInstance()

        # Get all attached devices and exit application if no device is found.
        # self.devices = self.tlFactory.EnumerateDevices()
        # if len(self.devices) == 0:
        #     raise IOError("No camera present.")
        # else:
        #     logger.debug("%d cameras found.", len(self.devices))

        # Connect camera
        # device_info = py.DeviceInfo()
        # device_info.SetIpAddress(ip)
        # # for device_info in self.devices:
        #     # if device_info.GetIpAddress() == ip:
        #         # logger.debug("Found camera on {}".format(ip))
        # self._cam_device = self.tlFactory.CreateDevice(device_info)
        # self._cam = py.InstantCamera(self._cam_device)
        # # assert self._cam.GetDeviceInfo().GetIpAddress() == ip
        #
        # # Let's start the fun
        # self._cam.StartGrabbing(py.GrabStrategy_LatestImageOnly)

    def loadConf(self, path):
        """Load configuration file (NodeMap.pfs)"""
        py.FeaturePersistence.Load(path, cameras[self.cam_idx].GetNodeMap())

    def saveConf(self, path):
        """Save camera status to NodeMap.pfs"""
        py.FeaturePersistence.Save(path, cameras[self.cam_idx].GetNodeMap())

    def grabImage(self):
        """Grab an image from the camera, ONE-BY-ONE MODE"""
        # self.cameras.PixelFormat = 'BGR8'

        # MUST set, TOTAL number of images to grab per camera !
        start_t = time.time()
        # Grab c_countOfImagesToGrab from the cameras.
        if not cameras[self.cam_idx].IsGrabbing():
            logger.debug("Camera is not in grabbing mode")
            return
        grabResult = cameras[self.cam_idx].RetrieveResult(
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
        logger.debug("Image grabbing time: %.02f", (end_t - start_t))
        return img

    def detach(self,):
        """Detach camera
        """
        cameras[self.cam_idx].DetachDevice()

    def setLight(self, status):
        """Set light on current camera (if applicable)
        We use GPIO here.
        See file:///Applications/pylon%20Programmer's%20Guide%20and%20API%20Reference.app/Contents/Resources/Html/class_pylon_1_1_c_basler_gig_e_camera.html
        """
        cameras[self.cam_idx].LineSelector.SetValue("Line3")
        cameras[self.cam_idx].LineInverter.SetValue(status)

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
