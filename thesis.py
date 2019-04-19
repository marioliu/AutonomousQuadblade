'''
Author: Mario Liu
Description: Module to do data processing for thesis writeup.
'''

from Camera import camera
from Algorithms import create_samples as cs
from Algorithms import discretize as ags
from Algorithms import rbf_interpolation as rbfi
from Algorithms import nav
from process_frames import plot2
from process_frames import getFramesFromSource

import matplotlib.pyplot as plt
import time
import math
import cv2
import numpy as np
from dronekit import connect
from pymavlink import mavutil

def dist_test():
    source = './Camera/Sample_Data/dist_comparison/25'
    d_25, c_25 = getFramesFromSource(source)

    source = './Camera/Sample_Data/dist_comparison/26'
    d_26, c_26 = getFramesFromSource(source)
    # figsize = width, height
    # figsize = (4.5, 5.5)

    fig = plt.figure()
    plt.subplot(2, 2, 1)
    plt.imshow(c_25)
    plt.title('Color Image at 25 Inches')
    plt.grid()

    plt.subplot(2, 2, 2)
    plt.imshow(d_25, cmap='gist_rainbow')
    plt.colorbar()
    plt.title('Depth Image at 25 Inches', y=1.04)
    plt.grid()

    plt.subplot(2, 2, 3)
    plt.imshow(c_26)
    plt.title('Color Image at 26 Inches')
    plt.grid()

    plt.subplot(2, 2, 4)
    plt.imshow(d_26, cmap='gist_rainbow')
    plt.colorbar()
    plt.title('Depth Image at 26 Inches', y=1.04)
    plt.grid()

    plt.subplots_adjust(hspace = 0.4)

    plt.show()

def outdoors():
    source = './Camera/Sample_Data/center_tree'
    d, c = getFramesFromSource(source)

    # figsize = width, height
    figsize = (6, 2.5)

    fig = plt.figure(figsize = figsize)
    plt.subplot(1, 2, 1)
    plt.imshow(c)
    plt.title('Color Image')
    plt.grid()

    plt.subplot(1, 2, 2)
    plt.imshow(d, cmap='gist_rainbow')
    plt.colorbar(fraction = 0.046, pad = 0.04)
    plt.title('Depth Image')
    plt.grid()

    plt.subplots_adjust(hspace = 0.4)

    plt.show()

def frame_comp():
    frames = np.array([1, 5, 10, 15, 20, 25, 30, 35, 40, 45, 50, 55, 60])
    numPixels = 640 * 480
    percent = []

    for i in frames:
        source = './Camera/Sample_Data/frame_comparison/' + str(i)
        d, c = getFramesFromSource(source)
        nonNan = np.count_nonzero(~np.isnan(d))
        percentage = float(nonNan*100)/numPixels
        percent.append(percentage)
        print('Number, % for {0} = ({1} & {2})'.format(i, nonNan, percentage))

    # polynomial fit onto data
    # p = np.poly1d(np.polyfit(frames, percent, 1))
    # xp = np.linspace(0, 60, 100)

    plt.scatter(frames, percent, c='r', label='Experimental Data')
    # plt.plot(xp, p(xp), label='Polynomial Fit')
    plt.title('Percentage of Usable Depth Data vs. Number of Frames')
    plt.ylabel('Percentage of Non-NaN Data')
    plt.xlabel('Number of Frames')
    plt.xlim([0, 60])
    plt.ylim([20, 55])
    # plt.legend()
    plt.grid()
    plt.show()

    ###### for comparing 1 frame vs 60 frames
    # source = './Camera/Sample_Data/frame_comparison/1'
    # d_1, c_1 = getFramesFromSource(source)

    # source = './Camera/Sample_Data/frame_comparison/60'
    # d_60, c_60 = getFramesFromSource(source)

    # # figsize = width, height
    # figsize = (6, 2.5)

    # fig = plt.figure(figsize = figsize)
    # plt.subplot(1, 2, 1)
    # plt.imshow(d_1, cmap='gist_rainbow')
    # plt.title('Depth Data (1 Frame)')
    # plt.grid()

    # plt.subplot(1, 2, 2)
    # plt.imshow(d_60, cmap='gist_rainbow')
    # plt.title('Depth Data (60 Frames)')
    # plt.grid()

    # plt.subplots_adjust(wspace = 0.4, hspace = 0.4)

    # plt.show()

def timing():
    source = './Camera/Sample_Data/center_tree'
    d, c = getFramesFromSource(source)
    notNan = 0
    t1 = time.time()
    for i in range(len(d)):
        for j in range(len(d[0])):
            if not np.isnan(d[i, j]): notNan += 1
    t2 = time.time()
    
    print('notNan = {0}'.format(notNan))
    print('time = {0}'.format(t2-t1))

def scale():
    max_depth = 6.0
    cam = camera.Camera(max_depth = max_depth)
    source = './Camera/Sample_Data/random_stuff'
    d, c = getFramesFromSource(source)
    d_small = cam.reduceFrame(d, height_ratio = 1, sub_sample = 0.3, reduce_to = 'lower')
    print('Size of d_small = ({0}, {1})'.format(len(d_small), len(d_small[0])))

    # figsize = width, height
    figsize = (6, 2.5)

    fig = plt.figure(figsize = figsize)
    plt.subplot(1, 2, 1)
    plt.imshow(d, cmap='gist_rainbow')
    plt.title('Original Depth Matrix')
    plt.grid()

    plt.subplot(1, 2, 2)
    plt.imshow(d_small, cmap='gist_rainbow')
    # plt.colorbar(fraction = 0.046, pad = 0.04)
    plt.title('Scaled Depth Matrix (30%)')
    plt.grid()

    plt.subplots_adjust(hspace = 0.4)

    plt.show()

def interp_comp():
    from Algorithms import create_samples
    from Algorithms import voronoi
    from Algorithms import rbf_interpolation

    max_depth = 6.0
    perc_samples = 0.01
    cam = camera.Camera(max_depth = max_depth)
    source = './Camera/Sample_Data/random_stuff'
    d, c = getFramesFromSource(source)
    d_small = cam.reduceFrame(d, height_ratio = 1, sub_sample = 0.3, reduce_to = 'lower')

    samples, vec = create_samples.createSamples(d_small, perc_samples)
    voronoi = voronoi.getVoronoi(d_small.shape, samples, vec)
    linear = rbf_interpolation.interpolate(d_small.shape, samples, vec, ftype='linear')

    plt.figure()
    plt.subplot(2, 2, 1)
    plt.title('Color')
    plt.imshow(c)

    plt.subplot(2, 2, 2)
    plt.title('Scaled Depth')
    plt.imshow(d_small, cmap='plasma')
    plt.colorbar(fraction = 0.046, pad = 0.04)

    plt.subplot(2, 2, 3)
    plt.title('Natural Neighbor')
    plt.imshow(voronoi, cmap='plasma')
    plt.colorbar(fraction = 0.046, pad = 0.04)

    plt.subplot(2, 2, 4)
    plt.title('Linear RBF')
    plt.imshow(linear, cmap='plasma')
    plt.colorbar(fraction = 0.046, pad = 0.04)

    plt.subplots_adjust(hspace = 0.3, wspace = 0.3)
    plt.show()

def main():
    # dist_test()
    # outdoors()
    # frame_comp()
    # timing()
    # scale()
    interp_comp()

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        plt.close('all')
        print('\nCtrl-C was pressed, exiting...')