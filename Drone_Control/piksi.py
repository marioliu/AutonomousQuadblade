# Author: Nadir Noordin
# Description: A module that gets coordinates from the Piksi GPS.
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

def getData(portNum):
    '''
    Gets NED vector from Piksi GPS located at /dev/ttyUSB[portNum].
    If two Piksi GPSs are talking, NED vector is in meters.
    '''
    directory = '/dev/ttyUSB' + str(portNum)
    north = None
    east = None
    down = None

    # Open a connection to Piksi using the default baud rate (1Mbaud)
    try:
        with PySerialDriver(directory, baud=1000000) as driver:
            with Handler(Framer(driver.read, None)) as source:
                for msg, metadata in source.filter(SBP_MSG_BASELINE_NED):
                    north = msg.n * 1e-3
                    east = msg.e * 1e-3
                    down = msg.d * 1e-3

                    if north != None and east != None and down != None:
                        return north,east,down

    except Exception as e:
        print('Error: ' + str(e))
        return

def main():
    parser = argparse.ArgumentParser(
        description="Swift Navigation SBP Example.")
    parser.add_argument(
        "-p",
        "--port",
        default=['/dev/ttyUSB1'],
        nargs=1,
        help="specify the serial port to use.")
    args = parser.parse_args()

    # run the function to get data from the gps
    n, e, d = getData((args.port[0])[-1])

    print("%.4f,%.4f,%.4f" % (n, e, d))

if __name__ == "__main__":
    main()

