#!/usr/bin/env python
# encoding: utf-8
"""
test_model.py

Created by Pierre-Julien Grizel et al.
Copyright (c) 2016 NumeriCube. All rights reserved.

Basic data-science model and predictions
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

import cv2

import ecoclassifier
from ecoclassifier.material_classifier import MaterialClassifier

HERE = os.path.dirname(os.path.realpath(__file__))


def test_model_init():
    """Just test that I can test the model (!)
    """
    classifier = MaterialClassifier()
    img = cv2.imread("2019-04-05-09-51-29-998464-CAM192-168-0-31.png")
    assert classifier.classify(img) == classifier.CLASS_PE_HD_OPAQUE
