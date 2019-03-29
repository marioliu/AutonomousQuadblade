#!/usr/bin/python
'''
Adapted from https://github.com/intel-aero/meta-intel-aero/wiki/04-Autonomous-drone-programming-in-Python
Description: Hello world for drone
'''
from dronekit import connect, VehicleMode, LocationGlobalRelative
import time

def main():
    vehicle = connect('tcp:127.0.0.1:5760', wait_ready=False)
    print("Arming motors:")
    vehicle.mode    = VehicleMode("GUIDED")
    vehicle.armed   = True
    while not vehicle.armed:
    print("  Waiting for arming to be finished")
    time.sleep(1)
    print("Keeping motors armed for 5s")
    time.sleep(5)
    print("Disarming")
    vehicle.armed   = False

if __name__== "__main__":
    main()