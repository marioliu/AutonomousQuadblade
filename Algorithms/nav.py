'''
Adapted from https://github.com/IntelligentQuadruped, with permission
Description: Module to clean camera data and provide a direction to
move in.
'''
import numpy as np
from scipy import sparse
import matplotlib.pyplot as plt
import discretize as ags
import voronoi
import rbf_interpolation as rbfi
from create_samples import createSamples
import obstacle_avoid as oa
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
        elif alg_type == 'ags_only':
            filled = depth
        else:
            print('Specify an alg_type in nav.reconstructFrame()')
            exit(1)

        adapted = ags.depthCompletion(filled, iters)

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
        pos = oa.findLargestGap(depth, min_dist, barrier_h, DEBUG=self.debug)

        return pos

    def plot(self, depth, sample_img, filled, ags, cmap='plasma', b=True):
        """
        Will plot the original depth, interpolated depth, and the
        position of where the algorithm recommends to move.
        """
        plt.figure(figsize=(7, 5.5))
        plt.subplot(2, 2, 1)
        plt.title('Depth')
        plt.imshow(depth, cmap=cmap)
        plt.xticks(visible=False)
        plt.yticks(visible=False)
        plt.colorbar()

        plt.subplot(2, 2, 2)
        plt.imshow(sample_img, cmap=cmap)
        plt.title('Samples')
        plt.xticks(visible=False)
        plt.yticks(visible=False)
        plt.colorbar()

        plt.subplot(2, 2, 3)
        plt.imshow(filled, cmap=cmap)
        plt.title('RBF')
        plt.xticks(visible=False)
        plt.yticks(visible=False)
        plt.colorbar()

        plt.subplot(2, 2, 4)
        plt.imshow(ags, cmap=cmap)
        plt.title('RBF + AGS')
        plt.xticks(visible=False)
        plt.yticks(visible=False)
        plt.colorbar()

        plt.subplots_adjust(bottom=0.1, right=0.9, top=0.9, left=0.125)
        # cax = plt.axes([0.85, 0.1, 0.075, 0.8])
        # plt.colorbar(cax=cax)

        plt.show(block=~b)
        if b:
            time.sleep(b)
            plt.close()

if __name__ == "__main__":
    """
    Application example with visualization.
    """
    h = 6
    w = 9

    depth = 4 * np.random.rand(h, w)
    for _ in range(6):
        y, x = int(h * np.random.sample()), int(w * np.random.sample())
        depth[y, x] = np.nan

    nav = Navigation(True)
    sample_img, filled, adapted = nav.reconstructFrame(depth, 0.5, .5, 2)
    pos = nav.obstacleAvoid(adapted, 1)

    if pos == None:
        print('pos is None, setting it to half of width')
        pos = int(len(depth[0]) / 2)

    frac = pos/float(len(depth[0]))
    print('pos = {0}, frac = {1}'.format(pos, frac))

    nav.plot(depth, sample_img, filled, adapted)