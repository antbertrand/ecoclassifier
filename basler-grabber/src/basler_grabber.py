# coding: utf-8
import camera
import numpy as np
import cv2
import os
import time
import argparse

#TODO : Enslave lights

parser = argparse.ArgumentParser(description='Process some integers.')

parser.add_argument('-agrx', '--auto-gain-roi-x', type=int, default=2648,
                    help='The X offset')
parser.add_argument('-agry', '--auto-gain-roi-y', type=int, default=1736,
                    help='The Y offset')
parser.add_argument('-agrw', '--auto-gain-roi-width', type=int, default=200,
                    help='Width of ROI square')
parser.add_argument('-agrh', '--auto-gain-roi-height', type=int, default=200,
                    help='Height of ROI square')
parser.add_argument('-out', '--output-path', type=str, default='/var/basler_grabber/',
                    help='Height of ROI square')
args = parser.parse_args()

#Init ALL cameras
cam = camera.Camera()

#Auto Exposure mode (no ROI dependancy)
cam.setAutoExposure()
print ("Set Auto Exposure function")
#Set ROI
print ("Set ROI and Auto Brightness/WithBalance/Gain functions")
cam.ROI(args.auto_gain_roi_width, args.auto_gain_roi_height, args.auto_gain_roi_x, args.auto_gain_roi_y)

if __name__ == "__main__":
	while True:
		input("Press Enter to take pictures, press ctrl+c to exit.")
		cam.grabbingImage(args.output_path)
