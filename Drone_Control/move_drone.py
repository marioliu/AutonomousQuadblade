#!/usr/bin/python
'''
Author: Mario Liu
Description: Module used to fly the Intel Aero and plan missions.
Adapted from https://dev.px4.io/en/robotics/dronekit.html and http://python.dronekit.io/guide/taking_off.html
'''
from dronekit import connect, Command, VehicleMode, LocationGlobal, LocationGlobalRelative
from pymavlink import mavutil
import time, sys, argparse, math

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
    print("Autopilot capabilities (supports ftp): \n\t%s" % vehicle.capabilities.ftp)
    print("Global Location: \n\t%s" % vehicle.location.global_frame)
    print("Global Location (relative altitude): \n\t%s" % vehicle.location.global_relative_frame)
    print("Local Location: \n\t%s" % vehicle.location.local_frame)    #NED
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
    vehicle._master.mav.command_long_send(vehicle._master.target_system,\
            vehicle._master.target_component,\
                mavutil.mavlink.MAV_CMD_DO_SET_MODE,\
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
    earth_radius=6378137.0 # Radius of "spherical" earth

    # Coordinate offsets in radians
    dLat = dNorth/earth_radius
    dLon = dEast/(earth_radius*math.cos(math.pi*original_location.lat/180))

    # New position in decimal degrees
    newlat = original_location.lat + (dLat * 180/math.pi)
    newlon = original_location.lon + (dLon * 180/math.pi)

    return LocationGlobal(newlat, newlon, original_location.alt+alt)

def square(vehicle):
    # load commands
    cmds = vehicle.commands
    cmds.clear()
    home = vehicle.location.global_relative_frame

    # takeoff to 5 meters
    wp = get_location_offset_meters(home, 0, 0, 5)
    cmd = Command(0,0,0, mavutil.mavlink.MAV_FRAME_GLOBAL_RELATIVE_ALT,\
        mavutil.mavlink.MAV_CMD_NAV_TAKEOFF, 0, 1, 0, 0, 0, 0,\
            wp.lat, wp.lon, wp.alt)
    cmds.add(cmd)

    # move 5 meters north
    wp = get_location_offset_meters(wp, 5, 0, 0)
    cmd = Command(0,0,0, mavutil.mavlink.MAV_FRAME_GLOBAL_RELATIVE_ALT,\
        mavutil.mavlink.MAV_CMD_NAV_WAYPOINT, 0, 1, 0, 0, 0, 0,\
            wp.lat, wp.lon, wp.alt)
    cmds.add(cmd)

    # move 5 meters east
    wp = get_location_offset_meters(wp, 0, 5, 0)
    cmd = Command(0,0,0, mavutil.mavlink.MAV_FRAME_GLOBAL_RELATIVE_ALT,\
        mavutil.mavlink.MAV_CMD_NAV_WAYPOINT, 0, 1, 0, 0, 0, 0,\
            wp.lat, wp.lon, wp.alt)
    cmds.add(cmd)

    # move 5 meters south
    wp = get_location_offset_meters(wp, -5, 0, 0)
    cmd = Command(0,0,0, mavutil.mavlink.MAV_FRAME_GLOBAL_RELATIVE_ALT,\
        mavutil.mavlink.MAV_CMD_NAV_WAYPOINT, 0, 1, 0, 0, 0, 0,\
            wp.lat, wp.lon, wp.alt)
    cmds.add(cmd)

    # move 5 meters west
    wp = get_location_offset_meters(wp, 0, -5, 0)
    cmd = Command(0,0,0, mavutil.mavlink.MAV_FRAME_GLOBAL_RELATIVE_ALT,\
        mavutil.mavlink.MAV_CMD_NAV_WAYPOINT, 0, 1, 0, 0, 0, 0,\
            wp.lat, wp.lon, wp.alt)
    cmds.add(cmd)

    # land
    wp = get_location_offset_meters(home, 0, 0, 5)
    cmd = Command(0,0,0, mavutil.mavlink.MAV_FRAME_GLOBAL_RELATIVE_ALT,\
        mavutil.mavlink.MAV_CMD_NAV_LAND, 0, 1, 0, 0, 0, 0,\
            wp.lat, wp.lon, wp.alt)
    cmds.add(cmd)

    # upload mission
    print('Uploading mission')
    cmds.upload()
    time.sleep(2)

def upDown(vehicle):
    # load commands
    cmds = vehicle.commands
    cmds.clear()
    home = vehicle.location.global_relative_frame

    # takeoff to 3 meters
    wp = get_location_offset_meters(home, 0, 0, 3)
    cmd = Command(0,0,0, mavutil.mavlink.MAV_FRAME_GLOBAL_RELATIVE_ALT,\
        mavutil.mavlink.MAV_CMD_NAV_TAKEOFF, 0, 1, 0, 0, 0, 0,\
            wp.lat, wp.lon, wp.alt)
    cmds.add(cmd)

    # land
    wp = get_location_offset_meters(home, 0, 0, 3)
    cmd = Command(0,0,0, mavutil.mavlink.MAV_FRAME_GLOBAL_RELATIVE_ALT,\
        mavutil.mavlink.MAV_CMD_NAV_LAND, 0, 1, 0, 0, 0, 0,\
            wp.lat, wp.lon, wp.alt)
    cmds.add(cmd)

    # upload mission
    print('Uploading mission')
    cmds.upload()
    time.sleep(2)

def main():
    # parse connection argument
    connection_string = 'tcp:127.0.0.1:5760'
    parser = argparse.ArgumentParser()
    parser.add_argument("-c", "--connect", help="connection string")
    args = parser.parse_args()

    if args.connect:
        connection_string = args.connect
    
    groundspeed = 0.5

    # connect to vehicle
    vehicle = connect(connection_string, wait_ready=False)
    # getAttr(vehicle)
    vehicle.groundspeed = groundspeed

    MAV_MODE_AUTO = 4

    # checks that the home is set before continuing
    home = vehicle.location.global_relative_frame
    while home.alt == None or home.alt < 0:
        print(" Waiting for GPS lock...")
        time.sleep(1)
        home = vehicle.location.global_relative_frame
    print('Home coords: {0}'.format(home))
    
    # change to AUTO mode (for mission planning)
    PX4setMode(vehicle, MAV_MODE_AUTO)
    time.sleep(1)
    print('Mode: ' + str(vehicle.mode.name))

    # wp = get_location_offset_meters(home, a, b, c)
    # a = +north, -south
    # b = +east, -west
    # c = +up, -down
    upDown(vehicle)

    # arm vehicle
    print('Arming drone...')
    vehicle.armed = True

    # monitor mission execution
    nextwaypoint = vehicle.commands.next
    while nextwaypoint < len(vehicle.commands):
        if vehicle.commands.next > nextwaypoint:
            display_seq = vehicle.commands.next+1
            print("Moving to waypoint %s" % display_seq)
            nextwaypoint = vehicle.commands.next
        time.sleep(1)

    # wait for the vehicle to land
    while vehicle.commands.next > 0:
        time.sleep(1)

    # disarm vehicle
    print('Disarming drone...')
    vehicle.armed = False
    time.sleep(1)

    # close vehicle object before exiting script
    vehicle.close()
    time.sleep(1)

    print('Done')

if __name__== "__main__":
    main()