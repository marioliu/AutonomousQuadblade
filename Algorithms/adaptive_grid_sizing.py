'''
Adapted from https://github.com/IntelligentQuadruped, with permission
Description: Fills in gaps in the R200 depth camera output.

Performance: Number of calculations increase as set standard-deviation
(SIGMA) parameter decreases. A sigma of 450 allows a depth inaccuracy of
45cm.
'''

import numpy as np

def setSigma(matrix, num=2):
    """
    Sets starting sigma value by interpolating from emperically
    determined data from R200 camera. 

    Default is a 3 sigma to get 95% of the values. 
    """
    x = matrix[matrix > 0].mean()
    a, b = [0.07064656, -0.03890366]
    sigma = a*x + b
    return num*round(sigma, 3)

def split(matrix):
    """
    Splits matrix into 6 equally sized rectangles:
    upper {left|middle|right} and lower {left|middle|right}.

    Arg:
        matrix: numpy 2D depth matrix
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

def average(matrix, sigma, max_h):
    """
    Assigns mean of all non-zero values to each gridcell given that the 
    standard deviations is within bounds and the quarters don't split below
    the minimum grid cell size. Inaccuracy is likely around 10%, sigma of up
    to 500, when images include multiple objects of different depths close
    together.

    Args:
        matrix: numpy 2D depth matrix
        sigma: threshold value for standard deviation
        max_h: maximum allowable height of averaged depth blocks
    Returns:
        matrix: 2d depth matrix with approximated values
    """
    h,w = matrix.shape
    # if depth values are all too different
    if matrix[matrix > 0].std() > sigma and h >= max_h:
        submatrices = split(matrix)
        for i, submatrix in enumerate(submatrices):
            submatrices[i] = average(submatrix, sigma, max_h)
        
        row1 = np.hstack((submatrices[0],submatrices[1],submatrices[2]))
        row2 = np.hstack((submatrices[3],submatrices[4],submatrices[5]))

        stacked = np.vstack((row1, row2))
        return stacked

    # if depth values are all kind of close
    else:
        avg_depth_value = matrix[matrix > 0].mean()
        matrix = np.full((h,w), avg_depth_value)
        return matrix

def cleanup(matrix, n):
    """
    In case a grid cell is left with a 0.0 as mean value, this function
    assigns the value of the next non-zero grid cell to it.
    """
    x, y = np.asarray(np.isnan(matrix)).nonzero()
    w = len(matrix[0])
    for xc, yc in zip(x, y):
        higher = [xc, yc]
        lower = [xc, yc]

        pastBot = False
        pastTop = False
        while(True):
            if higher[1] + n < w:
                higher[1] = higher[1] + n
            else:
                pastBot = True

            if lower[1] - n > 0:
                lower[1] = lower[1] - n
            else:
                pastTop = True

            if (not np.isnan(matrix[xc, higher[1]])) or (not np.isnan(matrix[xc, lower[1]])):
                matrix[xc, yc] = matrix[xc, higher[1]] if not np.isnan(matrix[xc, higher[1]]) else matrix[lower[0], lower[1]]
                break

            if pastBot and pastTop:
                raise Exception('Depth camera\'s view is obstructed, scaled depth matrix is full of NaNs!')
    
    return matrix

def depthCompletion(d, min_sigma, max_h):
    """
    Manages the appropriate sequence of completion steps to determine a
    depth estimate for each matrix entry.
    
    Args:
        matrix: depth values as numpy array
        min_sigma: acceptable deviation within calculated depth fields
        max_h: maximum allowable height of averaged depth blocks
    """

    # Reduces outliers to a maximum value of 4.0 which is the max
    # sensitivity value of the R200 depth sensors.

    depth = d.copy()
    # std = setSigma(matrix)
    # min_sigma = std if min_sigma < std else min_sigma

    avg = average(depth, min_sigma, max_h)
    clean = cleanup(avg, max_h/2)
    return clean

if __name__ == "__main__":
    """
    Application example with visualization.
    """
    import matplotlib.pyplot as plt

    depth = 4*np.random.rand(6, 10)
    depth[1, 5] = np.nan
    depth[1, 6] = np.nan
    depth[depth>4.0] = 0.0

    dep_comp = depthCompletion(depth, .01, 2)

    plt.subplot(2, 1, 1)
    plt.imshow(depth)
    plt.subplot(2, 1, 2)
    plt.imshow(dep_comp)
    plt.show()

else:
    np.warnings.filterwarnings('ignore')




