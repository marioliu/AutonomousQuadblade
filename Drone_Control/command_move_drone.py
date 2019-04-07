#!/usr/bin/python
'''
Author: Mario Liu
Description: Module used to fly the Intel Aero and plan missions.
Adapted from https://dev.px4.io/en/robotics/dronekit.html and http://python.dronekit.io/guide/taking_off.html
'''
from dronekit import connect, Command, VehicleMode, LocationGlobal, LocationGlobalRelative
from pymavlink import mavutil
import time
import sys
import argparse
import math


def getAttr(vehicle):
    '''
    Outputs a vehicle's attributes.

    Parameters:
    ----------
    vehicle: instance of the Vehicle class
        Vehicle returned from dronekit.connect().

    Returns:
    -------
    Nothing.
    '''
    print('VEHICLE ATTRIBUTES')
    print('-------------------------------------')
    print("Autopilot Firmware version: \n\t%s" % vehicle.version)
    print("Autopilot capabilities (supports ftp): \n\t%s" %
          vehicle.capabilities.ftp)
    print("Global Location: \n\t%s" % vehicle.location.global_frame)
    print("Global Location (relative altitude): \n\t%s" %
          vehicle.location.global_relative_frame)
    print("Local Location: \n\t%s" % vehicle.location.local_frame)  # NED
    print("Attitude: \n\t%s" % vehicle.attitude)
    print("Velocity: \n\t%s" % vehicle.velocity)
    print("GPS: \n\t%s" % vehicle.gps_0)
    print("Groundspeed: \n\t%s" % vehicle.groundspeed)
    print("Airspeed: \n\t%s" % vehicle.airspeed)
    print("Gimbal status: \n\t%s" % vehicle.gimbal)
    print("Battery: \n\t%s" % vehicle.battery)
    print("EKF OK?: \n\t%s" % vehicle.ekf_ok)
    print("Last Heartbeat: \n\t%s" % vehicle.last_heartbeat)
    print("Rangefinder: \n\t%s" % vehicle.rangefinder)
    print("Rangefinder distance: \n\t%s" % vehicle.rangefinder.distance)
    print("Rangefinder voltage: \n\t%s" % vehicle.rangefinder.voltage)
    print("Heading: \n\t%s" % vehicle.heading)
    print("Is Armable?: \n\t%s" % vehicle.is_armable)
    print("System status: \n\t%s" % vehicle.system_status.state)
    print("Mode: \n\t%s" % vehicle.mode.name)    # settable
    print("Armed: \n\t%s" % vehicle.armed)    # settable
    print('-------------------------------------')


def PX4setMode(vehicle, mavMode=64):
    '''
    Sets a vehicle's mode through PX4.

    Parameters:
    ----------
    vehicle: instance of the Vehicle class
        Vehicle returned from dronekit.connect().
    mavMode: int
        Flight mode of Aero.
        https://github.com/PX4/Firmware/blob/master/Tools/mavlink_px4.py
        -------------------
        # 0b00000001 Reserved for future use.
        MAV_MODE_FLAG_CUSTOM_MODE_ENABLED = 1

        # 0b00000010 system has a test mode enabled. This flag
        # is intended for temporary system tests and should not
        # be used for stable implementations.
        MAV_MODE_FLAG_TEST_ENABLED = 2

        # 0b00000100 autonomous mode enabled, system finds its
        # own goal positions. Guided flag can be set or not,
        # depends on the actual implementation.
        MAV_MODE_FLAG_AUTO_ENABLED = 4

        # 0b00001000 guided mode enabled, system flies MISSIONs
        # and/or mission items.
        MAV_MODE_FLAG_GUIDED_ENABLED = 8

        # 0b00010000 system stabilizes electronically its
        # attitude (and optionally position). It needs however
        # further control inputs to move around.
        MAV_MODE_FLAG_STABILIZE_ENABLED = 16

        # 0b00100000 hardware in the loop simulation. All motors
        # and actuators are blocked, but internal software is
        # fully operational.
        MAV_MODE_FLAG_HIL_ENABLED = 32

        # 0b01000000 remote control input is enabled.
        MAV_MODE_FLAG_MANUAL_INPUT_ENABLED = 64

        # 0b10000000 MAV safety set to armed. Motors are enabled
        # / running / can start. Ready to fly.
        MAV_MODE_FLAG_SAFETY_ARMED = 128

    Returns:
    -------
    Nothing.
    '''
    vehicle._master.mav.command_long_send(vehicle._master.target_system,
                                          vehicle._master.target_component,
                                          mavutil.mavlink.MAV_CMD_DO_SET_MODE,
                                          0, mavMode, 0, 0, 0, 0, 0, 0)


def get_location_offset_meters(original_location, dNorth, dEast, alt):
    """
    Returns a LocationGlobal object containing the latitude/longitude `dNorth` and `dEast` metres from the
    specified `original_location`. The returned Location adds the entered `alt` value to the altitude of the `original_location`.
    The function is useful when you want to move the vehicle around specifying locations relative to
    the current vehicle position.
    The algorithm is relatively accurate over small distances (10m within 1km) except close to the poles.
    For more information see:
    http://gis.stackexchange.com/questions/2951/algorithm-for-offsetting-a-latitude-longitude-by-some-amount-of-meters
    """
    earth_radius = 6378137.0  # Radius of "spherical" earth

    # Coordinate offsets in radians
    dLat = dNorth/earth_radius
    dLon = dEast/(earth_radius*math.cos(math.pi*original_location.lat/180))

    # New position in decimal degrees
    newlat = original_location.lat + (dLat * 180/math.pi)
    newlon = original_location.lon + (dLon * 180/math.pi)

    return LocationGlobal(newlat, newlon, original_location.alt+alt)

# Function to arm and then takeoff to a user specified altitude


def arm_and_takeoff(vehicle, aTargetAltitude):

    print "Basic pre-arm checks"
    # Don't let the user try to arm until autopilot is ready
    # while not vehicle.is_armable:
    #     print " Waiting for vehicle to initialise..."
    #     time.sleep(1)

    print "Arming motors"
    # Copter should arm in GUIDED mode
    vehicle.mode = VehicleMode("GUIDED")
    vehicle.armed = True

    while not vehicle.armed:
        print " Waiting for arming..."
        time.sleep(1)

    print "Taking off!"
    vehicle.simple_takeoff(aTargetAltitude)  # Take off to target altitude

    # Check that vehicle has reached takeoff altitude
    while True:
        print " Altitude: ", vehicle.location.global_relative_frame.alt
        # Break and return from function just below target altitude.
        if vehicle.location.global_relative_frame.alt >= aTargetAltitude*0.95:
            print "Reached target altitude"
            break
        time.sleep(1)


def main():
        # from piksi import getData
        # portNum = 0
        # parse connection argument
    connection_string = 'tcp:127.0.0.1:5760'
    parser = argparse.ArgumentParser()
    parser.add_argument("-c", "--connect", help="connection string")
    args = parser.parse_args()

    if args.connect:
        connection_string = args.connect

    airspeed = 0.1
    groundspeed = 0.1

    # connect to vehicle
    vehicle = connect(connection_string, wait_ready=False)
    # getAttr(vehicle)f
    vehicle.airspeed = airspeed
    vehicle.groundspeed = groundspeed

    MAV_MODE = 8

    # checks that the home is set before continuing
    home = vehicle.location.global_relative_frame
    while home.alt == None:
        print(" Waiting for GPS lock...")
        time.sleep(1)
        home = vehicle.location.global_relative_frame
    print("home is: " + str(home))

    # change to AUTO mode (for mission planning)
    PX4setMode(vehicle, MAV_MODE)
    time.sleep(1)
    print('Mode: ' + str(vehicle.mode.name))

    # Initialize the takeoff sequence to 20m
    arm_and_takeoff(vehicle, 2)
    print("Take off complete")

    # Hover for 10 seconds
    time.sleep(5)


    print("Now let's land")
    vehicle.mode = VehicleMode("RTL")



if __name__ == "__main__":
    main()
