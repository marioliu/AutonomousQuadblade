'''
Author: Mario Liu
Description: Module used to sample from depth matrices.
'''

import time
import numpy as np
from scipy import sparse

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
    # vec = R*xGT

    '''
    faster way of getting depth values at indices in samples
    '''
    vec = []
    for i in samples:
        vec.append(xGT[i])

    return samples, vec

def main():
    import matplotlib.pyplot as plt

    h = 12
    w = 16
    perc_samples = 0.5

    depth = np.zeros((h, w))
    depth.fill(np.nan)
    for _ in range(int((h * w) * 0.4)):
        y, x = int(h * np.random.sample()), int(w * np.random.sample())
        depth[y, x] = 6.0 * np.random.sample()
    nonNan = depth[~np.isnan(depth)]

    t1 = time.time()
    samples, vec = createSamples(depth, perc_samples)
    t2 = time.time()
    print('Sampling fraction: ' + str(perc_samples))
    print('Time to create samples: ' + str(t2 - t1))
    print('frac of samples: ' + str(len(samples)/float(len(nonNan))))
    print('samples: ' + str(samples))
    print('vec: ' + str(vec))

    plt.figure()

    plt.title('Samples ({0}% of All Pixels)'.format(perc_samples * 100))
    plt.imshow(depth, cmap='plasma')
    plt.colorbar()

    # mark each sample with red dot
    for samp in samples:
        x = samp % w
        y = samp / w
        plt.plot(x, y, 'wo', markersize=5)
        plt.plot(x, y, 'ro', markersize=3)

    plt.show()

if __name__ == "__main__":
    main()