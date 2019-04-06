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

def avoidObs(cam, numFrames, height_ratio, sub_sample, reduce_to, nav, perc_samples, sigma, iters, min_dist):
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

    c = cv2.cvtColor(c, cv2.COLOR_RGB2BGR)

    # depth
    d_small = cv2.applyColorMap(d_small.astype(np.uint8), cv2.COLORMAP_RAINBOW)

    # rbf
    adapted = cv2.applyColorMap(adapted.astype(np.uint8), cv2.COLORMAP_RAINBOW)

    da = np.concatenate((d_small, adapted), axis=1)

    # cv2.imshow('', da)

    # time.sleep(1)

def moveToTarget(vehicle, n, e):
    '''
    Moves vehicle to target at (n, e).
    '''
    groundspeed = 0.5
    vehicle.groundspeed = groundspeed

    # checks that GPS lock is set before continuing
    home = vehicle.location.global_relative_frame
    while home.alt == None:
        print(" Waiting for GPS lock...")
        time.sleep(1)
        home = vehicle.location.global_relative_frame
    
    home = vehicle.location.global_relative_frame
    print('Home coords: {0}'.format(home))

    # wp = get_location_offset_meters(home, a, b, c)
    # a = +north, -south
    # b = +east, -west
    # c = +up, -down

    # arm vehicle
    print('Arming drone...')
    vehicle.armed = True

    # set velocities

    # disarm vehicle
    print('Disarming drone...')
    vehicle.armed = False
    time.sleep(1)

    # close vehicle object before exiting script
    vehicle.close()
    time.sleep(1)

    print('Done')

def main():
    ######################### set up image processing
    max_depth = 6.0
    cam = camera.Camera(max_depth=max_depth)
    cam.connect()
    source = cam
    print('Connected to R200 camera')
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
    # vehicle.home_location = vehicle.location.global_frame
    MAV_MODE_AUTO = 4
    # change to AUTO mode (for mission planning)
    md.PX4setMode(vehicle, MAV_MODE_AUTO)
    time.sleep(1)
    print('Mode: ' + str(vehicle.mode.name))
    #########################

    while True:
        avoidObs(cam, numFrames, height_ratio, sub_sample, reduce_to, n, perc_samples, sigma, iters, min_dist)
        # n, e, d = piksi.getData(0)
        # print('n, e, d = ({0}, {1}, {2})'.format(n, e, d))
        # moveToTarget(vehicle, n, e)
        # time.sleep(1)

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        plt.close('all')
        print('\nCtrl-C was pressed, exiting...')