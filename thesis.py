'''
Author: Mario Liu
Description: Module to do data processing for thesis writeup.
'''

from Camera import camera
from Algorithms import create_samples as cs
from Algorithms import adaptive_grid_sizing as ags
from Algorithms import rbf_interpolation as rbfi
from Algorithms import nav
from process_frames import plot2
from process_frames import getFramesFromSource

import matplotlib.pyplot as plt
import time
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

def main():
    # dist_test()
    outdoors()

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        plt.close('all')
        print('\nCtrl-C was pressed, exiting...')