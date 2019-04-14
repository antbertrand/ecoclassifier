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

import os
import logging

# Logging configuration
LOG_FORMAT = "[%(asctime)s] p%(process)-8s %(levelname)-8s {%(name)s:%(filename)s:%(lineno)d} - %(message)s"
logging.basicConfig(format=LOG_FORMAT, level=logging.DEBUG)

# Where am I
HERE = os.path.dirname(os.path.realpath(__file__))

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
# PLC_TABLE_BARCODE_STATUS_INDEX = None
PLC_TABLE_BARCODE_CONTENT_WRITE = 42
PLC_TABLE_BARCODE_CONTENT_INDEX = 4
PLC_TABLE_MATERIAL_CONTENT_WRITE = 42
PLC_TABLE_MATERIAL_CONTENT_INDEX = 36
PLC_TABLE_DEFECT_WRITE = 42
PLC_TABLE_DEFECT_INDEX = 68

# Command index
PLC_COMMAND_STOP = b"\x00\x00"  # Nothing to do
PLC_COMMAND_READ_BARCODE = b"\x00\x0b"  # Read barcode
PLC_COMMAND_LEARN_BARCODE = b"\x00\x15"  # Learn barcodes
PLC_COMMAND_READ_MATERIAL = b"\x00\x1f"
PLC_COMMAND_LEARN_MATERIAL = b"\x00\x29"

# Command answers
PLC_ANSWER_MAIN_LOOP = b"\x00\x00"
PLC_ANSWER_BARCODE_START = b"\x00\x0b"
PLC_ANSWER_BARCODE_DONE = b"\x00\x0c"
PLC_ANSWER_BARCODE_LEARN_START = b"\x00\x15"
PLC_ANSWER_BARCODE_LEARN_DONE = b"\x00\x16"
PLC_ANSWER_MATERIAL_LEARN_START = b"\x00\x29"
PLC_ANSWER_MATERIAL_LEARN_DONE = b"\x00\x2a"
PLC_ANSWER_MATERIAL_READ_START = b"\x00\x1f"
PLC_ANSWER_MATERIAL_READ_DONE = b"\x00\x20"
PLC_ANSWER_MATERIAL_EMPTY = b"\x00\x21"
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

# MATERIAL TYPES
# Code
# Matière
# 0 # Matière inconnue
# 1 # PET <1> clair
# 2 # PET <1> foncé
# 3 # PE-HD <2> opaque
# 4 # Acier // recyclable
# 5 # Alu //  recyclable
# 6 # ELA
# 7 # Carton / Cartonnette
# 8 # PVC <3>
# 9 # Plastique souple, clair et opaque sachet - film alimentaire –stick
# 10 # P P <5>
# 11 # Verre
# 12 # PET <1> Barquette opaque
# 13 # Papier emballage alimentaire
# 17 # P S E <6>
# 18 # PET <1> Barquette  clair
# 19 # P E L D  <4>
# 20 # PET <1> opaque
# 22 # Opercule aluminium
MATERIAL_CODE_UNKNOWN = b"0\x00"
MATERIAL_CODE_PET_LIGHT = b"1\x00"

# Cameras serial numbers
# HZ is for Horizontal (front-facing) cameras.
# VT is for Vertical (above the object) cameras.
CAMERA_HZ_SERIALS = ()
CAMERA_VT_SERIALS = ()

CAMERA_VT_IP = "192.168.0.31"
CAMERA_HZ_IP = "192.168.0.32"

CAMERA_VT_SETTINGS_PATH = os.path.join(HERE, "cameras", "vt_camera.pfs")
CAMERA_HZ_SETTINGS_PATH = os.path.join(HERE, "cameras", "hz_camera.pfs")
