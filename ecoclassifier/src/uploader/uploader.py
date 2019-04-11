#!/usr/bin/env python
# encoding: utf-8
"""
uploader.py

Created by Pierre-Julien Grizel et al.
Copyright (c) 2016 NumeriCube. All rights reserved.

Main dataset uploader (meant to be called with a cron)
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
import time
import signal
import logging

from azure.storage.file import FileService

# pylint: disable=F403
from ecoclassifier import settings


def main():
    """Main runtime"""
    while True:
        # Look into Azure
        file_service = FileService(
            account_name="majurca",
            sas_token="?st=2019-04-04T21%3A21%3A42Z&se=2020-04-05T21%3A21%3A00Z&sp=rwdl&sv=2018-03-28&sr=s&sig=fSZNp8KFDtZpwikWc%2FIHQRcOAbyRDqLmZfTn4W0J6x4%3D",
        )

        # Scan file, upload them one by one restlessly
        # Only upload root directory
        for root, dirs, files in os.walk(settings.GRAB_PATH):
            for fn in files:
                file_service.create_file_from_path(
                    "datasets", "acquisitions", fn, os.path.join(root, fn)
                )
                os.remove(os.path.join(root, fn))

        time.sleep(60)


# Main loop
if __name__ == "__main__":
    main()
