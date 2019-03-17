'''
Adapted from https://github.com/IntelligentQuadruped, with permission
Description: Module used to interpolate values of depth matrix.

Original paper: https://github.com/sparse-depth-sensing/sparse-depth-sensing
'''

import numpy as np
import time
from scipy import sparse
from scipy.interpolate import Rbf
import matplotlib.pyplot as plt

def createSamples(depth, perc_samples):
    '''
    Grabs samples from original data.
    Sparse identity matrices are used to conserve memory since identity
    matrices are mostly zeros.

    Args:
        depth: Depth matrix to grab samples from

        perc_samples: Percent sampling rate

    Returns:
        list: A list (of size less than or =
        perc_samples * # of cells in depth matrix)
        of flattened indices that correspond to non-NaN
        values in the given depth matrix

        list: The actual depth values at the indices
        given by the previous list
    '''
    '''
    Code adapted from sparse-depth-sensing/lib/sampling/createSamples.m
    '''
    if (perc_samples > 1.0) or (perc_samples < 0.0):
        print('perc_samples must be between 0 and 1')
        exit(1)
    
    height = depth.shape[0]
    width = depth.shape[1]
    N = height * width
    K = int(N * perc_samples)

    xGT = depth.flatten()
    # random sampling
    rand = np.random.permutation(N)[:K]
    # xGT[rand] permutes the xGT matrix according to the rand matrix, creates
    # a permuted matrix of size len(rand)
    a = np.isnan(xGT[rand])
    # rand[np.nonzero(~a)[0]] permutes the rand matrix according to the
    # nonzero(~a) matrix, creates a permuted matrix of size len(nonzero(~a))
    samples = rand[np.nonzero(~a)[0]]

    '''
    very slow way of getting depth values at indices in samples
    '''
    # Rfull = sparse.eye(N)
    # # for i in samples, takes the ith row from Rfull
    # R = Rfull.tocsr()[samples,:]
    # # scipy sparse matrix vector product, xGT is size n x 1
    # measured_vector = R*xGT

    '''
    faster way of getting depth values at indices in samples
    '''
    measured_vector = []
    for i in samples:
        measured_vector.append(xGT[i])

    return samples, measured_vector

def interpolateDepthImage(shape, samples, measured_vector, ftype='linear'):
    '''
    Constructs new depth image by interpolating known points. RBF
    is used to interpolate.
    
    Args:
        shape: Shape of the depth matrix

        samples: List of flattened indices of non-NaN values
        in depth matrix

        measured_vector: List of depth values at the indices
        given by the previous list

        ftype: Interpolation type given as str, these can be
        found on the scipy.interpolate.Rbf docs - default is
        'linear'

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

    rbfi = Rbf(Y_sample, Z_sample, measured_vector, function=ftype)
    interpolated = rbfi(Yq, Zq)

    return interpolated

def main():
    h = 6
    w = 9
    perc_samples = 1

    depth = np.zeros((h, w))
    depth.fill(np.nan)
    for _ in range(int((h * w) / 3)):
        y, x = int(h * np.random.sample()), int(w * np.random.sample())
        depth[y, x] = 4.0 * np.random.sample()

    t1 = time.time()
    samples, measured = createSamples(depth, perc_samples)
    interpolated = interpolateDepthImage(depth.shape, samples, measured)
    t2 = time.time()
    print('Time to create samples and interpolate: ' + str(t2 - t1))

    figsize = (6, 5.5)
    plt.figure(figsize = figsize)

    plt.subplot(2, 1, 1)
    plt.title('Original')
    plt.imshow(depth, cmap='plasma')
    plt.colorbar()
    
    plt.subplot(2, 1, 2)
    plt.title('Interpolated')
    plt.imshow(interpolated, cmap='plasma')
    plt.colorbar()

    plt.subplots_adjust(hspace = 0.4)
    plt.show()

if __name__== "__main__":
    main()