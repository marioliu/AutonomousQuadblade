"""
Adapted from https://github.com/IntelligentQuadruped, with permission
Description: Gathers sample RGB and depth images from the R200.
"""

import numpy as np
import os
import time
from file_support import ensureDir
import pyrealsense as pyrs
serv = pyrs.Service()
dev = serv.Device(device_id=0, streams=[pyrs.stream.DepthStream(fps=60), pyrs.stream.ColorStream(fps=60)])

path = './Sample_Data/'
path += "{}".format(time.strftime("%d_%b_%Y_%H:%M:%S", time.localtime()))
ensureDir(path)

for i in range(10):
    try:
        dev.wait_for_frames()

        d = dev.depth * dev.depth_scale * 1000  #16 bit numbers
        gray = np.expand_dims(d.astype(np.uint8), axis=2)
        f = os.path.join(path, "%d_d.npy"%(i))
        np.save(f,d)

        col = dev.color
        f = os.path.join(path, "%d_c.npy"%(i))
        np.save(f,col)

        time.sleep(0.1)
    
    except KeyboardInterrupt:
        break


