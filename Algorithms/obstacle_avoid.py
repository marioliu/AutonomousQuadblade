'''
Adapted from https://github.com/IntelligentQuadruped, with permission
Description: Module to clean camera data and provide an open direction
to move in.
'''
import numpy as np
import matplotlib.pyplot as plt

class __GapData:
    """
    Private Object that will keep track of current row data.
    """
    def __init__(self, row_i, start_i, end_i, n, frac_h):
        """
        Intitalize Camera object with following optional parameters:
            row_i			Number of frames to average over
            start_i 		Ratio of bottom part of image to keep
            end_i			Rescale image by sub_sample
            n				Upper values to keep in depth image
        """
        self.row_i = row_i
        self.start_i = start_i
        self.end_i = end_i
        self.n = n
        self.gap = None

    def compareGap(self, s, f):
        """
        Compare start, s, and finish, f, values with that of the current
        gaps values. If smaller, return false.
        """
        g = self.gap
        if g is not None:
            return abs(g[1]-g[0]) < abs(f-s)
        else:
            return True

    def setGap(self, s, f):
        """
        Save new gap if larger than the current saved one.
        """
        g = self.gap
        if g is None:
            self.gap = (s, f)
        else:
            if abs(f-s) > abs(g[1]-g[0]):
                self.gap = (s, f)

def __addNextRow(row, start, finish, data):
    """
    Private function that is used to recursively check the rows above to
    find if a gap matches up.
    """
    if row == data.n:
        data.setGap(start, finish)
        return

    args = np.argwhere(data.row_i == row)
    
    for i in args:
        s = start
        f = finish
        c = data.start_i[i][0]
        d = data.end_i[i][0]
        if s < d and f > c:
            if s < c:
                s = c
            if f > d:
                f = d
            if data.compareGap(s, f):
                __addNextRow(row+1, s, f, data)

    return

def findLargestGap(depth_og, min_dist, barrier_h=.5, min_gap=0, DEBUG=False):
    """
    Given depth image, find the largest gap that goes from the bottom of
    the image to the top. Use min_dist as threshold below which objects are 
    shown to be too close. Return the position in the middle of the largest
    gap.
    """
    depth = depth_og > min_dist # true where gap exists
    try:
        if np.sum(depth[int(barrier_h*depth.shape[0]):]) == 0:
            return None
    except:
        return None

    npad = ((0, 0), (1, 1))
    d_padded = np.pad(depth, pad_width=npad, mode='constant', constant_values=0)

    indices = np.nonzero(np.diff(d_padded))
    row_indices = indices[0][0::2] # row indices
    data = __GapData(row_indices, indices[1][0::2], indices[1][1::2],
        len(np.unique(row_indices)), barrier_h)

    __addNextRow(0, 0, np.inf, data)
    sf = data.gap
    if sf is None:
        return None
    if sf[1] - sf[0] < min_gap:
        return None

    if DEBUG: 
        plt.imshow(depth)
        plt.title('Obstacles')
        plt.show()

    return (sf[0]+sf[1])/2.

def main():
    '''
    Unit tests
    '''
    import matplotlib.pyplot as plt

    h = 6
    w = 9

    depth = 4 * np.random.rand(h, w)
    for _ in range(6):
        y, x = int(h * np.random.sample()), int(w * np.random.sample())
        depth[y, x] = np.nan

    x = findLargestGap(depth, 1, DEBUG=True)
    print('Position of gap: {0}'.format(x))
    if x == None:
        x = len(depth[0]) // 2

    plt.title('Original')
    plt.imshow(depth, cmap='plasma')
    plt.scatter(int(x), 2, color='k', marker='o')
    plt.margins(x=0)

    plt.show()

if __name__== "__main__":
    main()








