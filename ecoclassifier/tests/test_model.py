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


def test_model_init():
    """Just test that I can test the model (!)
    """
    import ecoclassifier
    from ecoclassifier.material_classifier import MaterialClassifier

    classifier = MaterialClassifier()
