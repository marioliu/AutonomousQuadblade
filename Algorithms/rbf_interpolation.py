'''
Adapted from https://github.com/IntelligentQuadruped, with permission
Description: Module used to interpolate values of depth matrix.

Original paper: https://github.com/sparse-depth-sensing/sparse-depth-sensing
'''

import numpy as np
import time
from scipy.interpolate import Rbf
import matplotlib.pyplot as plt

def interpolate(shape, samples, vec, ftype='linear'):
    '''
    Constructs new depth image by interpolating known points. RBF
    is used to interpolate.
    
    Args:
        shape: Shape of the depth matrix

        samples: List of flattened indices of non-NaN values
        in depth matrix

        vec: List of depth values at the indices
        given by the previous list

        ftype: Interpolation type given as str, these can be
        found on the scipy.interpolate.Rbf docs - default is
        'linear'

        * NOTE: samples and vec must be obtained from the function
        create_samples.createSamples()

    Returns:
        matrix: New interpolated depth matrix
    '''
    '''
    Code adapted from
    sparse-depth-sensing/lib/algorithm/linearInterpolationOnImage.m
    '''
    h = np.arange(0, shape[0])
    w = np.arange(0, shape[1])

    Yq, Zq = np.meshgrid(w, h)
    Y_sample = Yq.flatten()[samples]
    Z_sample = Zq.flatten()[samples]

    rbfi = Rbf(Y_sample, Z_sample, vec, function=ftype)
    interpolated = rbfi(Yq, Zq)

    return interpolated

def main():
    '''
    Unit tests
    '''
    from create_samples import createSamples

    h = 6
    w = 9
    perc_samples = 1

    depth = np.zeros((h, w))
    depth.fill(np.nan)
    for _ in range(int((h * w) / 3)):
        y, x = int(h * np.random.sample()), int(w * np.random.sample())
        depth[y, x] = 4.0 * np.random.sample()

    t1 = time.time()
    samples, vec = createSamples(depth, perc_samples)
    interpolated = interpolate(depth.shape, samples, vec)
    t2 = time.time()
    print('Time to create samples and interpolate: ' + str(t2 - t1))

    figsize = (6, 5.5)
    plt.figure(figsize = figsize)

    plt.subplot(2, 1, 1)
    plt.title('Original')
    plt.imshow(depth, cmap='plasma')
    plt.colorbar()
    
    plt.subplot(2, 1, 2)
    plt.title('RBF Interpolated')
    plt.imshow(interpolated, cmap='plasma')
    plt.colorbar()

    plt.subplots_adjust(hspace = 0.4)
    plt.show()

if __name__== "__main__":
    main()