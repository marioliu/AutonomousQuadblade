"""
Adapted from https://github.com/IntelligentQuadruped, with permission
Description: Gathers sample RGB and depth images from the R200.
"""

import numpy as np
import os
import time
import camera
from file_support import ensureDir
import pyrealsense as pyrs

def getSamples(max_depth=6.0, numFrames=5):
    '''
    Gets sample averaged frames from the R200 camera.
    '''
    
    path = './Sample_Data/'
    path += "{}".format(time.strftime("%d_%b_%Y", time.localtime()))
    ensureDir(path)

    # get frames
    cam = camera.Camera(max_depth = max_depth)
    cam.connect()
    time.sleep(2.5)

    t1 = time.time()
    d, c = cam.getFrames(numFrames, rgb=True)
    t2 = time.time()
    printStmt = 'Time to get {0} frames: ' + str(t2 - t1)
    print(printStmt.format(numFrames))

    # save frames
    i = int(1000 * np.random.sample())
    f = os.path.join(path, "%d_d.npy"%(i))
    np.save(f, d)
    f = os.path.join(path, "%d_c.npy"%(i))
    np.save(f, c)

def main():
    max_depth = 6.0
    numFrames = 5
    getSamples(max_depth, numFrames)

if __name__ == "__main__":
    main()