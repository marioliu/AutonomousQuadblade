# Author: Nadir Noordin

# Description: a function that gets coordinates from the piksi gps
# Adapted from simple.py provided by Swift Navigation 



# Copyright (C) 2015 Swift Navigation Inc.
# Contact: Fergus Noble <fergus@swiftnav.com>
#
# This source is subject to the license found in the file 'LICENSE' which must
# be be distributed together with this source. All other rights reserved.
#
# THIS CODE AND INFORMATION IS PROVIDED "AS IS" WITHOUT WARRANTY OF ANY KIND,
# EITHER EXPRESSED OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE IMPLIED
# WARRANTIES OF MERCHANTABILITY AND/OR FITNESS FOR A PARTICULAR PURPOSE.
"""
the :mod:`sbp.client.examples.simple` module contains a basic example of
reading SBP messages from a serial port, decoding BASELINE_NED messages and
printing them out.
"""


from sbp.client.drivers.pyserial_driver import PySerialDriver
from sbp.client import Handler, Framer
from sbp.client.loggers.json_logger import JSONLogger
from sbp.navigation import SBP_MSG_BASELINE_NED, MsgBaselineNED
import argparse
import time



portNum = 0


def getData(portNum):

    directory = '/dev/ttyUSB' + str(portNum)
    north = None
    east = None
    down = None
    # Open a connection to Piksi using the default baud rate (1Mbaud)
    with PySerialDriver(directory, baud=1000000) as driver:
        with Handler(Framer(driver.read, None )) as source:
            try:
                for msg, metadata in source.filter(SBP_MSG_BASELINE_NED):
                    north = msg.n * 1e-3
                    east = msg.e * 1e-3
                    down = msg.d * 1e-3


                    if north != None and east != None and down != None:
                        # Print out the N, E, D coordinates of the baseline
                        print("%.4f,%.4f,%.4f" % (msg.n * 1e-3, msg.e * 1e-3,
                                              msg.d * 1e-3))
                        return north,east,down

            except KeyboardInterrupt:
                pass


def main():
    parser = argparse.ArgumentParser(
        description="Swift Navigation SBP Example.")
    parser.add_argument(
        "-p",
        "--port",
        default=['/dev/ttyUSB0'],
        nargs=1,
        help="specify the serial port to use.")
    args = parser.parse_args()

    # run the function to get data from the gps
    getData(portNum)    



if __name__ == "__main__":
    main()

