'''
Author: Mario Liu
Adapted from https://github.com/IntelligentQuadruped, with permission
Description: Fills in gaps in the R200 depth camera output. Discretizes
a depth matrix.
'''

import numpy as np
import matplotlib.pyplot as plt

def _split(matrix):
    """
    Splits matrix into 4 equally sized rectangles:
    upper {left|right} and lower {left|right}.

    Arg:
        matrix: NumPy 2D depth matrix
    Returns:
        4 matrices in list
    """
    h, w = matrix.shape
    h_prime = int(h/2.0)
    w_prime = int(w/2.0)

    # quarter matrices
    upper_left = matrix[:h_prime, :w_prime]
    upper_right = matrix[:h_prime, w_prime:]
    lower_left = matrix[h_prime:, :w_prime]
    lower_right = matrix[h_prime:, w_prime:]

    return [upper_left, upper_right,\
        lower_left, lower_right]

def _average(matrix, iters):
    """
    Assigns mean of all non-zero/non-NaN values to each gridcell given
    that the blocks are smaller than the maximum allowable block height.

    Args:
        matrix: NumPy 2D depth matrix
        iters: Divides matrix into 4^iters equally-sized blocks
        by subdividing matrix into halves with each successive iter.
        (e.g. iter = 1, matrix is split in half; iter = 2, matrix is
        split into quarters)
    Returns:
        matrix: 2D depth matrix with approximated values
    """
    h, w = matrix.shape

    nonNans = matrix[~np.isnan(matrix)]
    if len(nonNans) == 0:
        return matrix

    if iters > 0:
        submatrices = _split(matrix)
        for i, submatrix in enumerate(submatrices):
            submatrices[i] = _average(submatrix, iters - 1)
        
        row1 = np.hstack((submatrices[0],submatrices[1]))
        row2 = np.hstack((submatrices[2],submatrices[3]))

        stacked = np.vstack((row1, row2))

        return stacked

    # if depth values are all kind of close
    else:
        avg_depth_value = nonNans.mean()
        matrix = np.full((h, w), avg_depth_value)

        return matrix

def _cleanup(matrix, n):
    """
    In case a grid cell is left with a NaN value, this function
    assigns the value of the closest non-zero/non-NaN grid cell
    to it.
    """
    y, x = np.asarray(np.isnan(matrix)).nonzero()
    h = len(matrix)
    
    for xc, yc in zip(x, y):
        higher = yc
        lower = yc

        pastBot = False
        pastTop = False

        # fill top --> bottom first
        while(True):
            if higher + n < h:
                higher = higher + n
            else:
                pastBot = True

            if lower - n >= 0:
                lower = lower - n
            else:
                pastTop = True

            botIsNan = np.isnan(matrix[higher, xc])
            topIsNan = np.isnan(matrix[lower, xc])
            if (not botIsNan) or (not topIsNan):
                # fill in NaN cell
                if not botIsNan:
                    matrix[yc, xc] = matrix[higher, xc]
                else:
                    matrix[yc, xc] = matrix[lower, xc]
                break
            
            if pastBot and pastTop:
                # print('Cannot fill (y, x) = ' + str((yc, xc)))
                break
    
    return matrix

def depthCompletion(d, iters):
    """
    Manages the appropriate sequence of completion steps to determine a
    depth estimate for each matrix entry.
    
    Args:
        matrix: Depth values as NumPy array
        min_sigma: Acceptable deviation within calculated depth fields
        iters: Divides matrix into a 4^iters equally-sized blocks
        by subdividing matrix into halves with each successive iter.
        (e.g. iter = 1, matrix is split in half; iter = 2, matrix is
        split into quarters)
    """
    if iters < 0:
        print('iters cannot be negative!')
        exit(1)
    
    depth = d.copy()
    
    h = len(depth) / (2 ** iters)
    # catches the case where subdivisions get too small
    if h < 1:
        h = 1
    avg = _average(depth, iters)
    clean = _cleanup(avg, h)

    return clean

if __name__ == "__main__":
    """
    Application example with visualization.
    """
    h = 12
    w = 16

    depth = 6.0 * np.random.rand(h, w)
    dep_0 = depthCompletion(depth, 0)
    avg = np.average(dep_0)
    print('Average of iters = 0: {0}'.format(avg))
    dep_1 = depthCompletion(depth, 1)
    dep_2 = depthCompletion(depth, 2)

    plt.figure()

    plt.subplot(2, 2, 1)
    plt.title('Original')
    plt.imshow(depth, cmap='plasma')
    plt.colorbar(fraction = 0.046, pad = 0.04)

    plt.subplot(2, 2, 2)
    plt.title('Discretization, iters = {0}'.format(0))
    plt.imshow(dep_0, cmap='plasma')
    plt.colorbar(fraction = 0.046, pad = 0.04)

    plt.subplot(2, 2, 3)
    plt.title('Discretization, iters = {0}'.format(1))
    plt.imshow(dep_1, cmap='plasma')
    plt.colorbar(fraction = 0.046, pad = 0.04)

    plt.subplot(2, 2, 4)
    plt.title('Discretization, iters = {0}'.format(2))
    plt.imshow(dep_2, cmap='plasma')
    plt.colorbar(fraction = 0.046, pad = 0.04)

    plt.subplots_adjust(wspace = 0.4)
    plt.show()

else:
    np.warnings.filterwarnings('ignore')




