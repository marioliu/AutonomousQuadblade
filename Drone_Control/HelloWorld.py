#!/usr/bin/python
'''
Adapted from https://github.com/intel-aero/meta-intel-aero/wiki/04-Autonomous-drone-programming-in-Python and https://dev.px4.io/en/robotics/dronekit.html
Description: Hello world for drone
'''
from dronekit import connect, Command, VehicleMode, LocationGlobal, LocationGlobalRelative
from pymavlink import mavutil
import time, sys, argparse, math

def getAttr(vehicle):
    # vehicle is an instance of the Vehicle class
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

def PX4setMode(vehicle, mavMode):
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

    return LocationGlobal(newlat, newlon,original_location.alt+alt)

def main():
    # parse connection argument
    connection_string = 'tcp:127.0.0.1:5760'

    # SITL
    # import dronekit_sitl
    # sitl = dronekit_sitl.start_default()
    # connection_string = sitl.connection_string()

    parser = argparse.ArgumentParser()
    parser.add_argument("-c", "--connect", help="connection string")
    args = parser.parse_args()

    if args.connect:
        connection_string = args.connect
    
    groundspeed = 0.5

    # connect to vehicle
    vehicle = connect(connection_string, wait_ready=True, timeout=10)
    getAttr(vehicle)
    vehicle.groundspeed = groundspeed

    MAV_MODE_AUTO = 4

    # while not vehicle.is_armable:
    #     print(" Waiting for vehicle to initialise...")
    #     time.sleep(1)

    # change to AUTO mode
    PX4setMode(vehicle, MAV_MODE_AUTO)
    time.sleep(1)

    # load commands
    cmds = vehicle.commands
    cmds.clear()
    home = vehicle.location.global_relative_frame

    # takeoff to 0.5 meters
    wp = get_location_offset_meters(home, 0, 0, 0.5)
    cmd = Command(0,0,0, mavutil.mavlink.MAV_FRAME_GLOBAL_RELATIVE_ALT,\
        mavutil.mavlink.MAV_CMD_NAV_TAKEOFF, 0, 1, 0, 0, 0, 0,\
            wp.lat, wp.lon, wp.alt)
    cmds.add(cmd)

if __name__== "__main__":
    main()