'''
Author: Mario Liu
Description: Module to test the ODA algorithm and targeted landing.
'''

from Camera import camera
from Algorithms import create_samples as cs
from Algorithms import discretize as disc
from Algorithms import voronoi as voronoi
from Algorithms import gap_detection as gd
from process_frames import plot2
from Drone_Control import mission_move_drone as md
from process_frames import getFramesFromSource

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
        vehicle._master.target_system, vehicle._master.target_component,    # target system, target component
        # mavutil.mavlink.MAV_FRAME_LOCAL_NED, # frame
        mavutil.mavlink.MAV_FRAME_BODY_NED,
        0b0000111111000111, # type_mask (only speeds enabled)
        0, 0, 0, # x, y, z positions (not used)
        velocity_x, velocity_y, velocity_z, # x, y, z velocity in m/s
        0, 0, 0, # x, y, z acceleration (not supported yet, ignored in GCS_Mavlink)
        0, 0)    # yaw, yaw_rate (not supported yet, ignored in GCS_Mavlink)

    # send command to vehicle on 1 Hz cycle
    for x in range(0, duration):
        vehicle.send_mavlink(msg)
        time.sleep(1)

def avoidObs(cam, numFrames, height_ratio, sub_sample, reduce_to, perc_samples, iters, min_dist, DEBUG=False):
    # d = cam.getFrames(numFrames, rgb=False)

    # source = './Camera/Sample_Data/two_boxes'
    # d, c = getFramesFromSource(source)

    # generate representative depth matrix
    h = 12
    w = 16
    d = 6.0 * np.random.rand(h, w)

    t1 = time.time()

    d_small = cam.reduceFrame(d, height_ratio = height_ratio, sub_sample = sub_sample, reduce_to = reduce_to)

    samples, measured_vector = cs.createSamples(d_small, perc_samples)
    try:
        v = voronoi.getVoronoi(d_small.shape, samples, measured_vector)
    except:
        v = d_small
    d = disc.depthCompletion(v, iters)

    x = gd.findLargestGap(d, min_dist, DEBUG=DEBUG)

    t2 = time.time()
    print('t to process: {0}'.format(t2 - t1))

    if x == None:
        x = len(d[0]) // 2
    f = float(x)/len(d[0])
    print('(frac, position) of gap: ({0}, {1})'.format(f, x))

    delTheta = f * 59 - 29.5
    if f == 0.5:
        print('COMMAND: Move forward until an obstacle is detected\n')
    else:
        print('COMMAND: Rotate drone {0} degrees and move forward until obstacle is cleared\n'.format(delTheta))

    plt.figure()
    plt.imshow(d, cmap='plasma')
    plt.title('Navigation')
    plt.colorbar(fraction = 0.046, pad = 0.04)
    plt.plot([x, x], [len(d)-1, len(d)//2], 'r-', LineWidth=5)
    plt.plot([x, x], [len(d)-1, len(d)//2], 'w-', LineWidth=2)
    for i in range(len(d)//2, len(d)):
        plt.plot(int(x), i, 'wo', markersize=5)
        plt.plot(int(x), i, 'ro', markersize=3)

    plt.show()

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
    height_ratio = 1
    sub_sample = 1
    # reduce_to argFalseument can be: 'lower', 'middle_lower', 'middle', 'middle_upper', and 'upper'
    reduce_to = 'middle'
    # default of perc_samples = 0.01
    perc_samples = 1
    iters = 3
    min_dist = 1
    debug = False

    print('Program settings:')
    print('\tsource: ' + str(source))
    print('\tmax_depth: ' + str(max_depth))
    print('\tnumFrames: ' + str(numFrames))
    print('\theight_ratio: ' + str(height_ratio))
    print('\tsub_sample: ' + str(sub_sample))
    print('\treduce_to: ' + reduce_to)
    print('\tperc_samples: ' + str(perc_samples))
    print('\titers: ' + str(iters))
    print('\tmin_dist: ' + str(min_dist))
    print('\tdebug: ' + str(debug))

    #########################
    while True:
        avoidObs(cam, numFrames, height_ratio, sub_sample, reduce_to, perc_samples, iters, min_dist, DEBUG=debug)
    
    # ######################### set up drone connection
    # connection_string = 'tcp:127.0.0.1:5760'
    # vehicle = connect(connection_string, wait_ready=False)
    # # set home to current position (to hopefully make alt >= 0)
    # vehicle.home_location = vehicle.location.global_frame
    # MAV_MODE = 8
    # # change to MAV_MODE mode
    # md.PX4setMode(vehicle, MAV_MODE)
    # time.sleep(1)
    # print('Mode: ' + str(vehicle.mode.name))
    # #########################

    # # arm vehicle
    # print('Arming drone...')
    # vehicle.armed = True

    # try:
    #     while True:
    #         print('Going up...')
    #         send_ned_velocity(vehicle, 0, 0, -1, 4)
    #         print('Holding...')
    #         send_ned_velocity(vehicle, 0, 0, 0, 2)
    #         print('Going down...')
    #         send_ned_velocity(vehicle, 0, 0, 1, 4)
    #         print('Holding...')
    #         send_ned_velocity(vehicle, 0, 0, 0, 2)
    #         print('Disarming...')
    #         vehicle.armed = False
    #         time.sleep(1)
    #         return
    # except KeyboardInterrupt:
    #     # disarm vehicle
    #     print('Disarming drone...')
    #     vehicle.armed = False
    #     time.sleep(1)

    #     # close vehicle object before exiting script
    #     vehicle.close()
    #     time.sleep(1)

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        plt.close('all')
        print('\nCtrl-C was pressed, exiting...')