#!/usr/bin/env python
# encoding: utf-8
"""
plc.py

Created by Pierre-Julien Grizel et al.
Copyright (c) 2016 NumeriCube. All rights reserved.

Centralizes PLC communication
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


import logging

import snap7

from . import settings

# Logging configuration
logger = logging.getLogger(__name__)


class PLC(object):
    """PLC abstraction

    Sample session:
>>> import snap7
>>> sn = snap7.client.Client()
>>> sn.connect('192.168.0.1', 0, 1)

# This is before PLC has been configured correctly
>>> sn.db_read(42, 0, 1)
    """

    def __init__(
        self,
        address=settings.PLC_ADDRESS,
        rack=settings.PLC_RACK,
        slot=settings.PLC_SLOT,
    ):
        """Open connexion to the PLC.
        WARNING: there's no admitted re-entry.
        """
        # Connect
        self.client = snap7.client.Client()
        self.client.connect(address, rack, slot)

    def read(self, table, index, length=2):
        """Read from PLC"""
        return self.client.db_read(table, index, length)

    def write(self, table, index, content):
        """Write to PLC"""
        if isinstance(content, str):
            # This WILL raise Unicode errors, but remember we're only dealing with a PLC!
            content = bytes(content.encode("ascii"))
        elif isinstance(content, (bytearray, bytes)):
            pass
        else:
            raise NotImplementedError(
                "Don't know how to handle this type: {}".format(type(content))
            )
        return self.client.db_write(table, index, content)
