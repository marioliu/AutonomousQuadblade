'''
Author: Mario Liu
Description: Module to bring together and test all other modules.
'''

from Camera import camera
from Algorithms import create_samples as cs
from Algorithms import adaptive_grid_sizing as ags
from Algorithms import rbf_interpolation as rbfi
from Algorithms import nav
from process_frames import plot2
from Drone_Control import move_drone as md
from Drone_Control import piksi

import matplotlib.pyplot as plt
import time
import cv2
import numpy as np
from dronekit import connect
from pymavlink import mavutil

# copied from: http://python.dronekit.io/guide/copter/guided_mode.html
def send_ned_velocity(vehicle, velocity_x, velocity_y, velocity_z, duration):
    """
    Move vehicle in direction based on specified velocity vectors.
    velocity_z is positive towards the ground.
    """
    msg = vehicle.message_factory.set_position_target_local_ned_encode(
        0,       # time_boot_ms (not used)
        0, 0,    # target system, target component
        mavutil.mavlink.MAV_FRAME_LOCAL_NED, # frame
        0b0000111111000111, # type_mask (only speeds enabled)
        0, 0, 0, # x, y, z positions (not used)
        velocity_x, velocity_y, velocity_z, # x, y, z velocity in m/s
        0, 0, 0, # x, y, z acceleration (not supported yet, ignored in GCS_Mavlink)
        0, 0)    # yaw, yaw_rate (not supported yet, ignored in GCS_Mavlink)

    # send command to vehicle on 1 Hz cycle
    for x in range(0, duration):
        vehicle.send_mavlink(msg)
        time.sleep(1)

def avoidObs(vehicle, cam, numFrames, height_ratio, sub_sample, reduce_to, nav, perc_samples, sigma, iters, min_dist):
    t1 = time.time()

    d, c = cam.getFrames(numFrames, rgb=True)
    d_small = cam.reduceFrame(d, height_ratio = height_ratio, sub_sample = sub_sample, reduce_to = reduce_to)

    adapted = nav.reconstructFrame(d_small, perc_samples, sigma, iters)
    try:
        l = len(adapted)
    except:
        adapted = d_small

    pos = nav.obstacleAvoid(adapted, min_dist)
    if pos == None:
        pos = int(len(d_small[0]) / 2)

    frac = pos/float(len(d_small[0]))
    print('pos = {0}, frac = {1}'.format(pos, frac))

    t2 = time.time()

    print('Time for 1 iter: {0}\n'.format(t2 -t1))

def main():
    ######################### set up image processing
    max_depth = 6.0
    cam = camera.Camera(max_depth=max_depth)
    try:
        cam.connect()
        print('Connected to R200 camera')
    except:
        print('Cannot connect to camera')
        pass
    source = cam
    time.sleep(2.5)
    
    numFrames = 5
    # height_ratio of 1 keeps all rows of original image
    # default of h_r = 0.5, s_s = 0.3
    height_ratio = 0.5
    sub_sample = 0.3
    # reduce_to argument can be: 'lower', 'middle_lower', 'middle', 'middle_upper', and 'upper'
    reduce_to = 'middle'
    perc_samples = 0.05
    sigma = 0.2
    iters = 2
    min_dist = 2
    debug = False

    print('Program settings:')
    print('\tsource: ' + str(source))
    print('\tmax_depth: ' + str(max_depth))
    print('\tnumFrames: ' + str(numFrames))
    print('\theight_ratio: ' + str(height_ratio))
    print('\tsub_sample: ' + str(sub_sample))
    print('\treduce_to: ' + reduce_to)
    print('\tperc_samples: ' + str(perc_samples))
    print('\tsigma: ' + str(sigma))
    print('\titers: ' + str(iters))
    print('\tmin_dist: ' + str(min_dist))
    print('\tdebug: ' + str(debug))

    n = nav.Navigation(debug)
    #########################

    ######################### set up drone connection
    connection_string = 'tcp:127.0.0.1:5760'
    vehicle = connect(connection_string, wait_ready=False)
    # set home to current position (to hopefully make alt >= 0)
    vehicle.home_location = vehicle.location.global_frame
    MAV_MODE = 8
    # change to MAV_MODE mode
    md.PX4setMode(vehicle, MAV_MODE)
    time.sleep(1)
    print('Mode: ' + str(vehicle.mode.name))
    #########################

    # arm vehicle
    print('Arming drone...')
    vehicle.armed = True

    try:
        while True:
            # avoidObs(vehicle, cam, numFrames, height_ratio, sub_sample, reduce_to, n, perc_samples, sigma, iters, min_dist)
            print('Going up...')
            send_ned_velocity(vehicle, 0, 0, -0.1, 3)
            print('Going down...')
            send_ned_velocity(vehicle, 0, 0, 0.1, 3)
            print('Disarming...')
            vehicle.armed = False
            time.sleep(1)
            return
    except KeyboardInterrupt:
        # disarm vehicle
        print('Disarming drone...')
        vehicle.armed = False
        time.sleep(1)

        # close vehicle object before exiting script
        vehicle.close()
        time.sleep(1)

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        plt.close('all')
        print('\nCtrl-C was pressed, exiting...')