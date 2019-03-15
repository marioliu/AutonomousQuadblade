'''
Author: Mario Liu
Description: Module to test algorithms.
'''

from Camera import camera
from Algorithms import adaptive_grid_sizing as ags
from Algorithms import sparse_interpolation as si
import matplotlib.pyplot as plt
import time
import scipy as sp

def main():
    '''
    Test each gap algorithm one by one.
    '''

    '''
    preprocessing and grabbing frames
    '''
    max_depth = 4.0
    numFrames = 10
    # height_ratio of 0 crops 0 rows away
    height_ratio = 0.5
    sub_sample = 0.3
    # reduce_to argument can be: 'lower', 'middle_lower', 'middle', 'middle_upper', and 'upper'
    reduce_to = 'middle_lower'

    cam = camera.Camera(max_depth = max_depth)
    cam.connect()
    time.sleep(2.5)

    t1 = time.time()
    d = cam.getFrames(numFrames)
    t2 = time.time()
    cam.disconnect()
    printStmt = 'Time to get {0} frames: ' + str(t2 - t1)
    print(printStmt.format(numFrames))
    d_small = cam.reduceFrame(d, height_ratio = height_ratio, sub_sample = sub_sample, reduce_to = reduce_to)

    print('Program settings:')
    print('\tmax_depth: ' + str(max_depth))
    print('\tnumFrames: ' + str(numFrames))
    print('\theight_ratio: ' + str(height_ratio))
    print('\tsub_sample: ' + str(sub_sample))
    print('\treduce_to: ' + reduce_to)
    
    '''
    regular cropping and resizing
    '''
    # colormap:
    # https://matplotlib.org/tutorials/colors/colormaps.html

    # scaled depth
    fig1 = plt.figure(figsize = (6, 7)) # figsize = width, height
    ax2 = plt.subplot(2, 1, 2)
    plt.imshow(d_small, cmap='gist_rainbow')
    plt.colorbar()
    plt.title('Scaled (height_ratio = {0}, sub_sample = {1})'.format(height_ratio, sub_sample))
    plt.grid()

    # original depth
    # plt.subplot(2, 1, 1, sharex=ax2, sharey=ax2)
    plt.subplot(2, 1, 1)
    plt.imshow(d, cmap='gist_rainbow')
    plt.colorbar()
    plt.title('Original')
    plt.grid()

    plt.subplots_adjust(hspace = 0.3)

    fig1.show()

    '''
    adaptive grid sizing (recon)
    '''
    t1 = time.time()
    recon = ags.depthCompletion(d_small, 0.4, 20)
    t2 = time.time()
    print('Time to do AGS: ' + str(t2 - t1))

    fig2 = plt.figure(figsize = (6, 7))
    plt.subplot(2, 1, 1)
    plt.imshow(d_small, cmap='gist_rainbow')
    plt.colorbar()
    plt.title('Scaled (height_ratio = {0}, sub_sample = {1})'.format(height_ratio, sub_sample))
    plt.grid()

    plt.subplot(2, 1, 2)
    plt.imshow(recon, cmap='gist_rainbow')
    plt.colorbar()
    plt.title('Adaptive Grid Sizing (AGS) (Recon)')
    plt.grid()

    fig2.show()

    '''
    radial basis function
    '''
    samples, measured_vector = si.createSamples(d_small, 0.01)
    t1 = time.time()
    rbf_pre = si.interpolateDepthImage(d_small.shape, samples, measured_vector)
    rbf = ags.depthCompletion(rbf_pre, 0.2, 30)
    t2 = time.time()
    print('Time to do RBF and AGS: ' + str(t2 - t1))

    fig3 = plt.figure(figsize = (6, 7))
    plt.subplot(2, 1, 1)
    plt.imshow(d_small, cmap='gist_rainbow')
    plt.colorbar()
    plt.title('Scaled (height_ratio = {0}, sub_sample = {1})'.format(height_ratio, sub_sample))
    plt.grid()

    plt.subplot(2, 1, 2)
    plt.imshow(rbf, cmap='gist_rainbow')
    plt.colorbar()
    plt.title('RBF and AGS')
    plt.grid()

    fig3.show()

    # block plots until exited
    plt.show()

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print('\nCtrl-C was pressed, exiting...')