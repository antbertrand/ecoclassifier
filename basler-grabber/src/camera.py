# coding: utf-8
import pypylon.pylon as py
import numpy as np
import cv2
import datetime


class Camera(object):
    def __init__(self):
        # Get the transport layer factory.
        self.tlFactory = py.TlFactory.GetInstance()

        self.maxCamerasToUse = 2
        # Get all attached devices and exit application if no device is found.
        self.devices = self.tlFactory.EnumerateDevices()
        if len(self.devices) == 0:
            raise pylon.RUNTIME_EXCEPTION("No camera present.")
        else:
            print(len(self.devices), " cameras trouvées")

        # Create an array of instant cameras for the found devices and avoid exceeding a maximum number of devices.
        self.cameras = py.InstantCameraArray(
            min(len(self.devices), self.maxCamerasToUse)
        )

        self.l = self.cameras.GetSize()
        # Create and attach all Pylon Devices.
        for i, cam in enumerate(self.cameras):
            cam.Attach(self.tlFactory.CreateDevice(self.devices[i]))

            print("Using device ", cam.GetDeviceInfo().GetModelName())
        self.cameras.StartGrabbing(py.GrabStrategy_LatestImages)

        # self.cameras.PixelFormat = 'RGB8'

        # To load conf file NodeMap.pfs

    def loadConf(self):
        py.FeaturePersistence.Load(self.conf, self.instant_camera.GetNodeMap())
        return "Config Loaded"

        # To save conf file NodeMap.pfs

    def saveConf(self):
        py.FeaturePersistence.Save(self.conf, self.instant_camera.GetNodeMap())
        return "Config Saved"

    def ROI(self, width, height, offsetX, offsetY):
        # ROI is like a square(define by width and height)
        # moving by offset settings (define by OffsetX and OffsetY)
        # For Auto - Brightness/WithBalance/Gain adjust ON THE ROI
        # settings GainAuto and BalanceWhitAuto MUST be set in Continuous mode

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
        # To set Auto Exposure in Continuous Mode
        for cam in self.cameras:
            cam.ExposureAuto.SetValue("Continuous")

    def setAutoGain(self):
        # To set Auto Gain in Continuous Mode
        for cam in self.cameras:
            cam.GainAuto.SetValue("Continuous")

    def setAutoWhiteBalance(self):
        # To set AutoWhiteBalance in Continuous Mode
        for cam in self.cameras:
            cam.BalanceWhiteAuto.SetValue("Continuous")

        # For grab images

    def grabbingImage(self, path):

        # self.cameras.PixelFormat = 'BGR8'

        # MUST set, TOTAL number of images to grab per camera !
        countOfImagesToGrab = 1
        # Grab c_countOfImagesToGrab from the cameras.
        for i in range(countOfImagesToGrab):
            if not self.cameras.IsGrabbing():
                break
            for cam in self.cameras:

                grabResult = cam.RetrieveResult(5000, py.TimeoutHandling_ThrowException)

                # When the cameras in the array are created the camera context value
                # is set to the index of the camera in the array.
                # The camera context is a user settable value.
                # This value is attached to each grab result and can be used
                # to determine the camera that produced the grab result.
                cameraContextValue = grabResult.GetCameraContext()

                # Print the index and the model name of the camera.
                print(
                    "Camera ",
                    cameraContextValue,
                    ": ",
                    self.cameras[cameraContextValue].GetDeviceInfo().GetModelName(),
                )

                # Now, the image data can be processed.
                print("GrabSucceeded: ", grabResult.GrabSucceeded())
                print("SizeX: ", grabResult.GetWidth())
                print("SizeY: ", grabResult.GetHeight())
                img = grabResult.GetArray()
                print("Gray value of first pixel: ", img[0, 0])

                Camera.saveImage(self, img, cameraContextValue, path)

    def saveImage(self, img, camera_id, path):
        # make filename like yyyy-mm-dd-hh-mm-ss-nn-cam_id.png
        time = str(datetime.datetime.today())
        time = time.replace(" ", "-")
        time = time.replace(":", "-")
        time = time.replace(".", "-")
        # convert image to good RGB pixel format
        img = cv2.cvtColor(img, cv2.COLOR_BAYER_RG2RGB)
        # Save image tyo specified path
        cv2.imwrite("./" + time + "-CAM" + str(camera_id) + ".png", img)
