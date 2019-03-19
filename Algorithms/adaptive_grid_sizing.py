'''
Adapted from https://github.com/IntelligentQuadruped, with permission
Description: Fills in gaps in the R200 depth camera output.
'''
'''
Performance: Number of calculations increase as set standard-deviation
(SIGMA) parameter decreases. A sigma of 450 allows a depth inaccuracy of
45cm.
'''

import numpy as np
import matplotlib.pyplot as plt

def _setSigma(matrix, num=2):
    """
    Sets starting sigma value by interpolating from emperically
    determined data from R200 camera. 

    Default is a 3 sigma to get 95% of the values. 
    """
    x = matrix[matrix > 0].mean()
    a, b = [0.07064656, -0.03890366]
    sigma = a*x + b
    return num*round(sigma, 3)

def _split(matrix):
    """
    Splits matrix into 6 equally sized rectangles:
    upper {left|middle|right} and lower {left|middle|right}.

    Arg:
        matrix: NumPy 2D depth matrix
    Returns:
        6 matrices in list
    """
    h, w = matrix.shape
    h_prime = int(h/2)
    w_prime = int(w/3)

    # quarter matrices
    upper_left = matrix[:h_prime, :w_prime]
    upper_middle = matrix[:h_prime, w_prime:2*w_prime]
    upper_right = matrix[:h_prime, 2*w_prime:w]
    lower_left = matrix[h_prime:, :w_prime]
    lower_middle = matrix[h_prime:, w_prime:2*w_prime]
    lower_right = matrix[h_prime:, 2*w_prime:w]

    return [upper_left, upper_middle, upper_right,\
        lower_left, lower_middle, lower_right]

def _average(matrix, sigma, iters):
    """
    Assigns mean of all non-zero/non-NaN values to each gridcell given
    that the standard deviation is within bounds and the blocks are
    smaller than the maximum allowable block height. Inaccuracy is likely
    around 10%, sigma of up to 500, when images include multiple objects
    of different depths close together.

    Args:
        matrix: NumPy 2D depth matrix
        sigma: Threshold value for standard deviation
        iters: Divides matrix into a maximum of 2^iters vertical blocks
        by subdividing matrix into halves with each successive iter.
        (e.g. iter = 1, matrix is split in half; iter = 2, matrix is
        split into quarters)
    Returns:
        matrix: 2D depth matrix with approximated values
    """
    h, w = matrix.shape

    # if depth values are all too different
    if matrix[matrix > 0].std() > sigma and iters > 0:
        submatrices = _split(matrix)
        for i, submatrix in enumerate(submatrices):
            submatrices[i] = _average(submatrix, sigma, iters - 1)
        
        row1 = np.hstack((submatrices[0],submatrices[1],submatrices[2]))
        row2 = np.hstack((submatrices[3],submatrices[4],submatrices[5]))

        stacked = np.vstack((row1, row2))

        return stacked

    # if depth values are all kind of close
    else:
        avg_depth_value = matrix[matrix > 0].mean()
        matrix = np.full((h, w), avg_depth_value)

        return matrix

def _cleanup(matrix, n):
    """
    In case a grid cell is left with a NaN value, this function
    assigns the value of the closest non-zero/non-NaN grid cell
    to it.
    """
    x, y = np.asarray(np.isnan(matrix)).nonzero()
    w = len(matrix[0])
    for xc, yc in zip(x, y):
        higher = yc
        lower = yc

        pastBot = False
        pastTop = False

        while(True):
            if higher + n < w:
                higher = higher + n
            else:
                pastBot = True

            if lower - n > 0:
                lower = lower - n
            else:
                pastTop = True

            botIsNan = np.isnan(matrix[xc, higher])
            topIsNan = np.isnan(matrix[xc, lower])
            if (not botIsNan) or (not topIsNan):
                # fill in NaN cell
                if not botIsNan:
                    matrix[xc, yc] = matrix[xc, higher] 
                else:
                    matrix[xc, yc] = matrix[xc, lower]
                break
            # TODO: CHECK LEFT/RIGHT SO THIS DOESN'T GET STUCK IN LOOP
            if pastBot and pastTop:
                matrix[xc, yc] = np.nan
                break
    
    return matrix

def depthCompletion(d, min_sigma, iters):
    """
    Manages the appropriate sequence of completion steps to determine a
    depth estimate for each matrix entry.
    
    Args:
        matrix: Depth values as NumPy array
        min_sigma: Acceptable deviation within calculated depth fields
        iters: Divides matrix into a maximum of 2^iters vertical blocks
        by subdividing matrix into halves with each successive iter.
        (e.g. iter = 1, matrix is split in half; iter = 2, matrix is
        split into quarters)
    """

    # Reduces outliers to a maximum value of 4.0 which is the max
    # sensitivity value of the R200 depth sensors.

    depth = d.copy()
    # std = _setSigma(matrix)
    # min_sigma = std if min_sigma < std else min_sigma
    
    avg = _average(depth, min_sigma, iters)
    h = len(depth) / (2 ** iters)
    # catches the case where subdivisions get too small
    if h < 1:
        h = 1
    clean = _cleanup(avg, h)

    return clean

if __name__ == "__main__":
    """
    Application example with visualization.
    """
    h = 6
    w = 9

    depth = 4 * np.random.rand(h, w)
    for _ in range(5):
        y, x = int(h * np.random.sample()), int(w * np.random.sample())
        depth[y, x] = np.nan

    dep_comp = depthCompletion(depth, .01, 5)

    figsize = (6, 5.5)
    plt.figure(figsize = figsize)

    plt.subplot(2, 1, 1)
    plt.title('Original')
    plt.imshow(depth, cmap='plasma')
    plt.colorbar()

    plt.subplot(2, 1, 2)
    plt.title('Filled-In Matrix')
    plt.imshow(dep_comp, cmap='plasma')
    plt.colorbar()

    plt.subplots_adjust(hspace = 0.4)
    plt.show()

else:
    np.warnings.filterwarnings('ignore')




