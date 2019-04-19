'''
Author: Mario Liu
Description: Helper module for retrieving and showing data.
'''

import time
import os
import numpy as np
import matplotlib.pyplot as plt

def getFramesFromSource(source, numFrames=5):
    '''
    Gets frames from either a data directory or from the camera itself.

    Args:
        source: Can be either a Camera object or a path to a
        directory of .npy files

    Returns:
        One depth matrix and one color matrix
    '''

    # assuming source is a Camera object
    try:
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

            if 'c.npy' in file:
                c = frame
            elif 'd.npy' in file:
                d = frame

        return d, c
    except Exception as e:
        print('Error: ' + str(e))
        raise Exception('source must a Camera object or a path to a directory of .npy files!')

def plot2(figs, m1, m2, title1, title2):
    '''
    Takes in two numpy matrices and plots them with a `gist_rainbow`
    colormap.

    Args:
        figs: List to store figures in
        m1: First numpy matrix to plot
        m2: Second numpy matrix to plot
        title1: Title of first plot
        title2: Title of second plot

    Returns:
        Nothing
    '''
    # figsize = width, height
    figsize = (6, 5.5)
    # colormap:
    # https://matplotlib.org/tutorials/colors/colormaps.html

    fig = plt.figure(figsize = figsize)
    figs.append(fig)
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

def main():
    '''
    Tests each algorithm one by one.
    '''
    import sys
    from Camera import camera
    from Algorithms import discretize as disc
    from Algorithms import rbf_interpolation as rbfi
    from Algorithms import voronoi as voro
    from Algorithms import create_samples as cs

    argv = sys.argv
    if len(argv) == 1:
        print('Usage: python {0} [cam|data]'.format(argv[0]))
        exit(1)

    max_depth = 6.0
    cam = camera.Camera(max_depth = max_depth)
    source = None
    if argv[1] == 'cam':
        cam.connect()
        source = cam
        print('Connected to R200 camera')
    elif argv[1] == 'data':
        print('Using data directory for frames')
        source = './Camera/Sample_Data/two_boxes'
    else:
        print('Usage: python {0} [cam|data]'.format(argv[0]))
        exit(1)

    numFrames = 60
    # height_ratio of 1 keeps all rows of original image
    # default of h_r = 0.5, s_s = 0.3
    height_ratio = 1
    sub_sample = 0.3
    # reduce_to argument can be: 'lower', 'middle_lower', 'middle', 'middle_upper', and 'upper'
    reduce_to = 'middle'
    iters = 2
    perc_samples = 0.01

    print('Program settings:')
    print('\tsource: ' + str(source))
    print('\tmax_depth: ' + str(max_depth))
    print('\tnumFrames: ' + str(numFrames))
    print('\theight_ratio: ' + str(height_ratio))
    print('\tsub_sample: ' + str(sub_sample))
    print('\treduce_to: ' + reduce_to)
    print('\titers: ' + str(iters))

    #######################################################
    # test algorithms and plot
    #######################################################
    # sleep to make sure camera starts up
    time.sleep(2.5)
    d, c = getFramesFromSource(source, numFrames)
    d_small = cam.reduceFrame(d, height_ratio = height_ratio, sub_sample = sub_sample, reduce_to = reduce_to)

    # uncomment to plot original image
    fig0 = plt.figure()
    plt.imshow(c)
    plt.title('Color Image')
    plt.grid()
    fig0.show()

    figs = []
    scaledTitle = 'Scaled (height_ratio = {0}, sub_sample = {1})'.format(height_ratio, sub_sample)

    # regular cropping and resizing
    plot2(figs, d, d_small, 'Original', scaledTitle)

    # initial discretization
    t1 = time.time()
    recon = disc.depthCompletion(d_small, iters)
    t2 = time.time()

    print('Time to do disc: ' + str(t2 - t1))
    print('')
    plot2(figs, d_small, recon, scaledTitle, 'Discretization')

    # use when rbf fails
    # raw_input('Press <Enter> to close all plots and exit')
    # return
    
    # radial basis function
    t1 = time.time()
    samples, measured_vector = cs.createSamples(d_small, perc_samples)
    try:
        rbf = rbfi.interpolate(d_small.shape, samples, measured_vector)
    except:
        rbf = d_small
    t2 = time.time()
    rbf_disc = disc.depthCompletion(rbf, iters)
    t3 = time.time()

    print('Time to do RBF: ' + str(t2 - t1))
    plot2(figs, d_small, rbf, scaledTitle, 'RBF')

    print('Time to do RBF and disc: ' + str(t3 - t1))
    print('')
    plot2(figs, d_small, rbf_disc, scaledTitle, 'RBF and disc')

    # Voronoi interpolation
    t1 = time.time()
    samples, measured_vector = cs.createSamples(d_small, perc_samples)
    try:
        v = voro.getVoronoi(d_small.shape, samples, measured_vector)
    except:
        v = d_small
    t2 = time.time()
    voro_disc = disc.depthCompletion(v, iters)
    t3 = time.time()

    print('Time to do Voronoi: ' + str(t2 - t1))
    plot2(figs, d_small, v, scaledTitle, 'Voronoi')

    print('Time to do Voronoi and disc: ' + str(t3 - t1))
    print('')
    plot2(figs, d_small, voro_disc, scaledTitle, 'Voronoi and disc')

    # block plots until button is pressed
    raw_input('Press <Enter> to close all plots and exit')

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        plt.close('all')
        print('\nCtrl-C was pressed, exiting...')