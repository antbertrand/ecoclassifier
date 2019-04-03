#!/usr/bin/env python
# encoding: utf-8
"""
settings.py

Created by Pierre-Julien Grizel et al.
Copyright (c) 2016 NumeriCube. All rights reserved.

Global settings file
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

# Table informations
PLC_TABLE_HEARTBEAT_READ = 1
PLC_TABLE_COMMAND_READ = 2
PLC_TABLE_HEARTBEAT_WRITE = 3
PLC_TABLE_BARCODE_WRITE = 4
PLC_TABLE_BARCODE_CONTENT = 5
PLC_TABLE_MATERIAL_WRITE = 6
PLC_TABLE_MATERIAL_CONTENT = 7
PLC_TABLE_DEFECT = 8

# Command index
PLC_COMMAND_STOP = 0  # Nothing to do
PLC_COMMAND_READ_BARCODE = 1  # Read barcode
PLC_COMMAND_LEARN_BARCODE = 11
PLC_COMMAND_READ_MATERIAL = 2
PLC_COMMAND_LEARN_MATERIAL = 22

# Cameras serial numbers
# HZ is for Horizontal (front-facing) cameras.
# VT is for Vertical (above the object) cameras.
CAMERA_HZ_SERIALS = ()

CAMERA_VT_SERIALS = ()
