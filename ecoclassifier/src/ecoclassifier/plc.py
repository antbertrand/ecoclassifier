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

# Logging configuration
logFormatter = "[%(asctime)s] p%(process)-8s %(levelname)-8s {%(pathname)s:%(lineno)d} - %(message)s"
logging.basicConfig(format=logFormatter, level=logging.DEBUG)
logger = logging.get_logger(__name__)


class PLC(object):
    """PLC abstraction

    Sample session:
>>> import snap7
>>> sn = snap7.client.Client()
>>> sn.connect('192.168.0.1', 0, 1)

# This is before PLC has been configured correctly
>>> sn.db_read(42, 0, 1)
    """

    def __init__(self, address, param0=0, param1=1):
        """Open connexion to the PLC.
        WARNING: there's no admitted re-entry.
        """
        # Connect
        self.client = snap7.client.Client()
        self.client.connect(address, param0, param1)

    def read(self, table, length=1):
        """Read from PLC"""
        return self.client.db_read(table, 0, length)

    def write(self, table, content):
        """Write to PLC"""
        if isinstance(content, str):
            # This WILL raise Unicode errors, but remember we're only dealing with a PLC!
            content = content.encode("ascii")
        else:
            raise NotImplementedError(
                "Don't know how to handle this type: {}".format(type(content))
            )
        return self.client.db_write(table, 0, content)
