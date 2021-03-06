# Taken from https://github.com/basler/pypylon/blob/master/samples/imageeventprinter.py
from pypylon import pylon


class ImageEventPrinter(pylon.ImageEventHandler):
    def OnImagesSkipped(self, camera, countOfSkippedImages):
        print(
            "OnImagesSkipped event for device ", camera.GetDeviceInfo().GetModelName()
        )
        print(countOfSkippedImages, " images have been skipped.")
        print()

    def OnImageGrabbed(self, camera, grabResult):
        print("OnImageGrabbed event for device ", camera.GetDeviceInfo().GetModelName())

        # Image grabbed successfully?
        if grabResult.GrabSucceeded():
            print("SizeX: ", grabResult.GetWidth())
            print("SizeY: ", grabResult.GetHeight())
            img = grabResult.GetArray()
            print("Gray values of first row: ", img[0])
            print()
        else:
            print(
                "Error: ", grabResult.GetErrorCode(), grabResult.GetErrorDescription()
            )
