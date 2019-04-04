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


# Logging configuration
# XXX TODO

# Output path
GRAB_PATH = "/home/majurca/var/acquisitions"

# Loop configuration
MAIN_LOOP_POOLING_WAIT_SECONDS = 1
BARCODE_POOLING_WAIT_SECONDS = 0

# PLC configuration
PLC_ADDRESS = "192.168.0.1"
PLC_RACK = 0
PLC_SLOT = 1

# Table informations
PLC_TABLE_HEARTBEAT_READ = 43
PLC_TABLE_HEARTBEAT_WRITE = 42
PLC_TABLE_HEARTBEAT_INDEX = 0
PLC_TABLE_HEARTBEAT_LENGTH = 2
PLC_TABLE_COMMAND_READ = 43
PLC_TABLE_COMMAND_INDEX = 2
PLC_TABLE_ANSWER_WRITE = 42
PLC_TABLE_ANSWER_INDEX = 2
PLC_TABLE_BARCODE_STATUS_WRITE = 42
PLC_TABLE_BARCODE_STATUS_INDEX = None
PLC_TABLE_BARCODE_CONTENT_WRITE = 42
PLC_TABLE_BARCODE_CONTENT_INDEX = 4
PLC_TABLE_MATERIAL_WRITE = 6
PLC_TABLE_MATERIAL_CONTENT = 7
PLC_TABLE_DEFECT = 8

# Command index
PLC_COMMAND_STOP = b"\x00\x00"  # Nothing to do
PLC_COMMAND_READ_BARCODE = b"\x00\x0b"  # Read barcode
PLC_COMMAND_LEARN_BARCODE = b"\x00\x15"  # Learn barcodes
PLC_COMMAND_READ_MATERIAL = 2
PLC_COMMAND_LEARN_MATERIAL = 22

# Command answers
PLC_ANSWER_MAIN_LOOP = b"\x00\x00"
PLC_ANSWER_BARCODE_START = b"\x00\x0a"
PLC_ANSWER_BARCODE_DONE = b"\x00\x0b"
PLC_ANSWER_BARCODE_LEARN_START = b"\x00\x15"
PLC_ANSWER_BARCODE_LEARN_DONE = b"\x00\x16"
# 0 arrêté
# 11 - lecture code barre lancée
# 12 – code barre lu
# 21 - apprentissages Code barre lancés
# 22 - apprentissages Code barre terminés
# 31 - lecture lancée
# 32 - code matière lu
# 33 – pas de code matière
# 41 – apprentissages lancés
# 42 – apprentissages terminés

# Cameras serial numbers
# HZ is for Horizontal (front-facing) cameras.
# VT is for Vertical (above the object) cameras.
CAMERA_HZ_SERIALS = ()
CAMERA_VT_SERIALS = ()

CAMERA_VT_IP = "192.168.0.31"
CAMERA_HZ_IP = "192.168.0.32"
