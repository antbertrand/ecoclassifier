#!/usr/bin/env python
# encoding: utf-8
"""
ecoclassifier.py

Created by Pierre-Julien Grizel et al.
Copyright (c) 2016 NumeriCube. All rights reserved.

Main eco-classifier entry point
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
import logging

import sentry_sdk
import tenacity

# pylint: disable=F403
from . import settings
from . import plc

# Configure Sentry
sentry_sdk.init(os.environ["SENTRY_URL"])

# Configure logging
# logFormatter = "%(asctime)s %(name)-12s %(message)s"
logFormatter = "[%(asctime)s] p%(process)-8s %(levelname)-8s {%(pathname)s:%(lineno)d} - %(message)s"
logging.basicConfig(format=logFormatter, level=logging.DEBUG)
logger = logging.getLogger(__name__)
logger.info("Starting Ecoclassifier module.")


class Ecoclassifier(object):
    """Main singleton for our Ecoclassifier program
    """

    def heartbeat(self,):
        """Provide a simple heartbeat
        """
        heartbeat = self.client.read(
            settings.PLC_TABLE_HEARTBEAT_READ,
            settings.PLC_TABLE_HEARTBEAT_INDEX,
            settings.PLC_TABLE_HEARTBEAT_LENGTH,
        )
        self.client.write(
            settings.PLC_TABLE_HEARTBEAT_WRITE,
            settings.PLC_TABLE_HEARTBEAT_INDEX,
            heartbeat,
        )

    def get_plc_command(self,):
        """Get command to execute from our PLC
        """
        return self.client.read(
            settings.PLC_TABLE_COMMAND_READ, settings.PLC_TABLE_COMMAND_INDEX
        )

    def read_barcode(self,):
        """Try to read barcode.
        """

    @tenacity.retry(
        wait=tenacity.wait_exponential(multiplier=1, min=2, max=600),
        after=tenacity.after_log(logger, logging.DEBUG),
    )
    def run(self,):
        """Main loop"""
        try:
            # Connect PLC
            self.client = plc.PLC(settings.PLC_ADDRESS)

            while True:
                # Heartbeat
                logger.debug("Entering loop!")
                self.heartbeat()

                # Depending on the PLC status, decide what to do
                command = self.get_plc_command()
                if command == settings.PLC_COMMAND_STOP:
                    time.sleep(settings.MAIN_LOOP_POOLING_WAIT_SECONDS)
                elif command == 1:
                    continue
                else:
                    raise NotImplementedError("Invalid command: {}".format(command))

        except Exception as e:
            logger.exception("Exception in main loop")
            sentry_sdk.capture_exception(e)
            raise


def main():
    """Main runtime"""
    ec = Ecoclassifier()
    exit(ec.run())


# Main loop
if __name__ == "__main__":
    main()
