'''
Adapted from https://github.com/IntelligentQuadruped, with permission
Description: Module to clean camera data and provide a direction to
move in.
'''
import numpy as np
from scipy import sparse
import matplotlib.pyplot as plt
import discretize as disc
import voronoi
import rbf_interpolation as rbfi
from create_samples import createSamples
import gap_detection as gd
import time
import logging

class Navigation:
    """
    Object to use depth images to find gap to move in to.
    """

    def __init__(self, debug=False):
        """
        Intitalize Navigation object
        """
        self.debug = debug

    def reconstructFrame(self, depth, perc_samples=0.01, iters=2, alg_type='rbf'):
        """
        Given a partial depth image, will return a reconstructed version filling
        in all missing data.
        """
        samples, measured_vector = createSamples(depth, perc_samples)

        if alg_type == 'voronoi':
            if len(samples) <= 1:
                return None
            filled = voronoi.getVoronoi(depth.shape, samples, measured_vector)
        elif alg_type == 'rbf':
            if len(samples) <= 1:
                return None
            filled = rbfi.interpolate(depth.shape, samples, measured_vector)
        elif alg_type == 'disc_only':
            filled = depth
        else:
            print('Specify an alg_type in nav.reconstructFrame()')
            exit(1)

        adapted = disc.depthCompletion(filled, iters)

        if self.debug:
            sample_img = np.zeros((depth.shape)).flatten()
            sample_img.fill(np.nan)
            sample_img[samples] = depth.flatten()[samples]
            sample_img = sample_img.reshape(depth.shape)

            return sample_img, filled, adapted
        
        return adapted
    
    def obstacleAvoid(self, depth, min_dist=1.0, barrier_h=.5):
        """
        Given a depth image and a threshold value, will find the largest gap
        that can be used, returning the position along the image's width where
        it is.
        """
        pos = gd.findLargestGap(depth, min_dist, barrier_h, DEBUG=self.debug)

        return pos

    def plot(self, depth, sample_img, filled, disc, cmap='plasma', b=True):
        """
        Will plot the original depth, interpolated depth, and the
        position of where the algorithm recommends to move.
        """
        plt.figure()
        y = 1.04

        plt.subplot(2, 2, 1)
        plt.title('Depth', y=y)
        plt.imshow(depth, cmap=cmap)
        plt.colorbar(fraction = 0.046, pad = 0.04)

        plt.subplot(2, 2, 2)
        plt.imshow(sample_img, cmap=cmap)
        plt.title('Samples', y=y)
        plt.colorbar(fraction = 0.046, pad = 0.04)

        plt.subplot(2, 2, 3)
        plt.imshow(filled, cmap=cmap)
        plt.title('Natural Neighbor', y=y)
        plt.colorbar(fraction = 0.046, pad = 0.04)

        plt.subplot(2, 2, 4)
        plt.imshow(disc, cmap=cmap)
        plt.title('Discretized Natural Neighbor', y=y)
        plt.colorbar(fraction = 0.046, pad = 0.04)

        plt.subplots_adjust(hspace = 0.3, wspace = 0.3)

        plt.show(block=~b)
        if b:
            time.sleep(b)
            plt.close()

if __name__ == "__main__":
    """
    Application example with visualization.
    """
    h = 12
    w = 16
    perc_samples = 0.3
    iters = 3

    depth = 6.0 * np.random.rand(h, w)
    for _ in range(int((h * w) * 0.6)):
        y, x = int(h * np.random.sample()), int(w * np.random.sample())
        depth[y, x] = np.nan

    nav = Navigation(True)
    sample_img, filled, adapted = nav.reconstructFrame(depth, perc_samples, iters, alg_type='voronoi')
    pos = nav.obstacleAvoid(adapted, 1)

    if pos == None:
        print('pos is None, setting it to half of width')
        pos = int(len(depth[0]) / 2)

    frac = pos/float(len(depth[0]))
    print('pos = {0}, frac = {1}'.format(pos, frac))

    nav.plot(depth, sample_img, filled, adapted)