'''
Author: Mario Liu
Description: Module to test algorithms.
'''

from Camera import camera
from Algorithms import adaptive_grid_sizing as ags
from Algorithms import sparse_interpolation as si
import matplotlib.pyplot as plt
import time
import os
import numpy as np
import scipy as sp

def plot2(figs, m1, m2, title1, title2):
    '''
    Takes in two numpy matrices and plots them with a `gist_rainbow`
    colormap.

    Args:
        figs: list to store figures in
        m1: first numpy matrix to plot
        m2: second numpy matrix to plot
        title1: title of first plot
        title2: title of second plot

    Returns:
        Nothing
    '''
    # figsize = width, height
    figsize = (6, 5.5)
    # colormap:
    # https://matplotlib.org/tutorials/colors/colormaps.html

    figs.append(plt.figure(figsize = figsize))
    plt.subplot(2, 1, 1)
    plt.imshow(m1, cmap='gist_rainbow')
    plt.colorbar()
    plt.title(title1)
    plt.grid()

    plt.subplot(2, 1, 2)
    plt.imshow(m2, cmap='gist_rainbow')
    plt.colorbar()
    plt.title(title2)
    plt.grid()

    plt.subplots_adjust(hspace = 0.3)

    figs[-1].show()

def getFramesFromSource(source, numFrames=10):
    '''
    Gets frames from either a data directory or from the camera itself.

    Args:
        source: can be either a Camera object or a path to a directory of
        .npy files

    Returns:
        One depth matrix and one color matrix
    '''

    # assuming source is a Camera object
    try:
        time.sleep(2.5)

        t1 = time.time()
        d, c = source.getFrames(numFrames, rgb=True)
        t2 = time.time()
        printStmt = 'Time to get {0} frames: ' + str(t2 - t1)
        print(printStmt.format(numFrames))

        return d, c
    except:
        pass

    # assuming source is a directory of .npy files
    try:
        d = 0
        c = 0
        for i, file in enumerate(os.listdir(source)):
            path = os.path.join(source, file)
            frame = np.load(str(path))
            if 'c' in file:
                c = frame
            else:
                d = frame

        return d, c
    except:
        raise Exception('source must a Camera object or a path to a directory of .npy files!')

def main():
    '''
    Test each algorithm one by one.
    '''

    cam = camera.Camera()
    cam.connect()

    # source = cam
    source = './Camera/Sample_Data/16_Mar_2019'

    max_depth = 4.0
    numFrames = 10
    # height_ratio of 0 crops 0 rows away
    height_ratio = 0.5
    sub_sample = 0.3
    # reduce_to argument can be: 'lower', 'middle_lower', 'middle', 'middle_upper', and 'upper'
    reduce_to = 'middle_lower'
    sigma = 0.2
    max_h = 30
    
    d, c = getFramesFromSource(source, numFrames)
    d_small = cam.reduceFrame(d, height_ratio = height_ratio, sub_sample = sub_sample, reduce_to = reduce_to)

    print('Program settings:')
    print('\tsource: ' + str(source))
    print('\tmax_depth: ' + str(max_depth))
    print('\tnumFrames: ' + str(numFrames))
    print('\theight_ratio: ' + str(height_ratio))
    print('\tsub_sample: ' + str(sub_sample))
    print('\treduce_to: ' + reduce_to)
    print('\tsigma: ' + str(sigma))
    print('\tmax_h: ' + str(max_h))

    #######################################################
    # test algorithms and plot
    #######################################################
    # uncomment to plot original image
    # fig0 = plt.figure()
    # plt.imshow(c)
    # plt.title('Color Image')
    # plt.grid()
    # fig0.show()

    figs = []
    scaledTitle = 'Scaled (height_ratio = {0}, sub_sample = {1})'.format(height_ratio, sub_sample)

    # regular cropping and resizing
    plot2(figs, d, d_small, 'Original', scaledTitle)

    # adaptive grid sizing (recon)
    t1 = time.time()
    recon = ags.depthCompletion(d_small, sigma, max_h)
    t2 = time.time()
    print('Time to do AGS: ' + str(t2 - t1))

    plot2(figs, d_small, recon, scaledTitle, 'Adaptive Grid Sizing (AGS) (Recon)')

    # radial basis function
    samples, measured_vector = si.createSamples(d_small, 0.01)
    t1 = time.time()
    rbf_pre = si.interpolateDepthImage(d_small.shape, samples, measured_vector)
    rbf = ags.depthCompletion(rbf_pre, sigma, max_h)
    t2 = time.time()
    print('Time to do RBF and AGS: ' + str(t2 - t1))

    plot2(figs, d_small, rbf, scaledTitle, 'RBF and AGS')

    # block plots until button is pressed
    raw_input('Press <Enter> to close all plots and exit')

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        plt.close('all')
        print('\nCtrl-C was pressed, exiting...')