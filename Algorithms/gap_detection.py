'''
Adapted from https://github.com/IntelligentQuadruped, with permission
Description: Module to do gap detection on a depth matrix.
'''
import numpy as np
import matplotlib.pyplot as plt

class __GapData:
    """
    Private Object that will keep track of current row data.
    """
    def __init__(self, row_i, start_i, end_i, n):
        """
        Parameters
        ----------
            row_i			Current row of GapData
            start_i 		Starting row
            end_i			End row
            n				
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
        len(np.unique(row_indices)))

    __addNextRow(0, 0, np.inf, data)
    sf = data.gap
    if sf is None:
        return None
    if sf[1] - sf[0] < min_gap:
        return None

    if DEBUG:
        plt.figure(figsize = (6, 2.5))
        plt.subplot(1, 2, 1)
        plt.imshow(depth)
        plt.title('Obstacles')
        plt.grid()

    return (sf[0]+sf[1])/2.

def main():
    '''
    Unit tests
    '''
    import matplotlib.pyplot as plt
    from create_samples import createSamples
    import voronoi
    import discretize as disc

    h = 12
    w = 16
    perc_samples = 0.3
    iters = 3

    depth = 6.0 * np.random.rand(h, w)
    for _ in range(int((h * w) * 0.6)):
        y, x = int(h * np.random.sample()), int(w * np.random.sample())
        depth[y, x] = np.nan

    samples, measured_vector = createSamples(depth, perc_samples)
    v = voronoi.getVoronoi(depth.shape, samples, measured_vector)
    d = disc.depthCompletion(v, iters)

    x = findLargestGap(d, 1, DEBUG=True)
    print('(frac, position) of gap: ({0}, {1})'.format(float(x)/len(d[0]), x))
    if x == None:
        x = len(d[0]) // 2

    plt.subplot(1, 2, 2)
    plt.imshow(d, cmap='plasma')
    plt.title('Gap Detection')
    plt.colorbar(fraction = 0.046, pad = 0.04)
    plt.plot([x, x], [len(d)-1, len(d)//2], 'r-', LineWidth=5)
    plt.plot([x, x], [len(d)-1, len(d)//2], 'w-', LineWidth=2)
    for i in range(len(d)//2, len(d)):
        plt.plot(int(x), i, 'wo', markersize=5)
        plt.plot(int(x), i, 'ro', markersize=3)
    
    plt.subplots_adjust(wspace = 0.3)

    plt.show()

if __name__== "__main__":
    main()








