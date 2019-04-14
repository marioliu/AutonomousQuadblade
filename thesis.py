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
from Drone_Control import mission_move_drone as md
from Drone_Control import piksi

import matplotlib.pyplot as plt
import time
import cv2
import numpy as np
from dronekit import connect
from pymavlink import mavutil

def main():
    pass

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        plt.close('all')
        print('\nCtrl-C was pressed, exiting...')