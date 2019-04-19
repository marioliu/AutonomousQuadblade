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
    import sys

    h = 12
    w = 16
    perc_samples = 0.3

    argv = sys.argv
    np.random.seed(54)
    depth = np.zeros((h, w))
    depth.fill(np.nan)
    for _ in range(int((h * w) * 0.4)):
        y, x = int(h * np.random.sample()), int(w * np.random.sample())
        depth[y, x] = 6.0 * np.random.sample()

    t1 = time.time()
    samples, vec = createSamples(depth, perc_samples)
    linear = interpolate(depth.shape, samples, vec, ftype='linear')
    t2 = time.time()
    thin_plate = interpolate(depth.shape, samples, vec, ftype='thin_plate')
    gaussian = interpolate(depth.shape, samples, vec, ftype='gaussian')
    multiquadric = interpolate(depth.shape, samples, vec, ftype='multiquadric')
    inv_multiquadric = interpolate(depth.shape, samples, vec, ftype='inverse')
    print('Time to create samples and interpolate: ' + str(t2 - t1))

    # figsize = (6, 2.5)
    plt.figure()

    y = 1.2
    plt.subplot(2, 3, 1)
    plt.title('Original', y=y)
    plt.imshow(depth, cmap='plasma')
    plt.colorbar(fraction = 0.046, pad = 0.04)
    
    plt.subplot(2, 3, 2)
    plt.title('Linear RBF', y=y)
    plt.imshow(linear, cmap='plasma')
    plt.colorbar(fraction = 0.046, pad = 0.04)

    plt.subplot(2, 3, 3)
    plt.title('Thin Plate Spline RBF', y=y)
    plt.imshow(thin_plate, cmap='plasma')
    plt.colorbar(fraction = 0.046, pad = 0.04)

    plt.subplot(2, 3, 4)
    plt.title('Gaussian RBF', y=y)
    plt.imshow(gaussian, cmap='plasma')
    plt.colorbar(fraction = 0.046, pad = 0.04)
    
    plt.subplot(2, 3, 5)
    plt.title('Multiquadric RBF', y=y)
    plt.imshow(multiquadric, cmap='plasma')
    plt.colorbar(fraction = 0.046, pad = 0.04)

    plt.subplot(2, 3, 6)
    plt.title('Inverse Multiquadric RBF', y=y)
    plt.imshow(inv_multiquadric, cmap='plasma')
    plt.colorbar(fraction = 0.046, pad = 0.04)

    # plt.figure()
    # x = range(h*w)
    # flat = interpolated.copy()
    # flat[1::2] = interpolated[1::2,::-1]
    # flat = flat.ravel()
    # plt.plot(x[0:w], flat[0:w])

    plt.subplots_adjust(wspace = 0.6)
    plt.show()

if __name__== "__main__":
    main()