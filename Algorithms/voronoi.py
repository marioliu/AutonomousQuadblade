'''
Adapted from https://github.com/IntelligentQuadruped, with permission
Description: Module used to interpolate values of depth matrix using
Voronoi interpolation.
'''

import numpy as np
import matplotlib.pyplot as plt
from scipy.spatial import Voronoi
from shapely.geometry import Polygon
from matplotlib.path import Path
from colorized_voronoi import voronoi_finite_polygons_2d

def getVoronoi(shape, samples, vec):
    '''
    Constructs new depth image by creating Voronoi regions.
    
    Args:
        shape: Shape of the depth matrix

        samples: List of flattened indices of non-NaN values
        in depth matrix

        vec: List of depth values at the indices
        given by the previous list

        * NOTE: samples and vec must be obtained from the function
        create_samples.createSamples()

    Returns:
        matrix: New depth matrix
    '''
    h, w = shape

    he = np.arange(0, h)
    wi = np.arange(0, w)

    Yq, Zq = np.meshgrid(wi, he)
    Y_sample = Yq.flatten()[samples]
    Z_sample = Zq.flatten()[samples]

    points = np.column_stack((Y_sample, Z_sample))
    voronoi = Voronoi(points)

    regions, vertices = voronoi_finite_polygons_2d(voronoi)
    reconstructed = np.zeros((w, h))
    b = Polygon([(0, 0), (w-1, 0), (w-1, h-1), (0, h-1)])

    reconstructed = np.zeros((w, h))

    for i, region in enumerate(regions):
        polygon = vertices[region]
        shape = Polygon(polygon)
        if not b.contains(shape):
            shape = shape.intersection(b)

        x, y = shape.exterior.coords.xy

        row_indices = np.array(x, dtype=np.int16)
        column_indices = np.array(y, dtype=np.int16)

        row_min = np.amin(row_indices)
        row_max = np.amax(row_indices) + 1
        column_min = np.amin(column_indices)
        column_max = np.amax(column_indices) + 1

        enclose = np.zeros((row_max-row_min, column_max-column_min))
        enclose_rows = row_indices-row_min
        enclose_columns = column_indices-column_min

        enclose[enclose_rows, enclose_columns] = 1 

        points = np.indices(enclose.shape).reshape(2, -1).T
        path = Path(zip(x-row_min,y-column_min))

        mask = path.contains_points(points, radius=-1e-9)
        mask = mask.reshape(enclose.shape)

        reconstructed_rows, reconstructed_columns = np.where(mask)

        reconstructed[row_min+reconstructed_rows, column_min+reconstructed_columns] = vec[i]

    return reconstructed.T

def main():
    """
    Application example with visualization.
    """
    import time
    from create_samples import createSamples

    h = 12
    w = 16
    perc_samples = 0.3

    depth = np.zeros((h, w))
    depth.fill(np.nan)
    for _ in range(int((h * w) * 0.4)):
        y, x = int(h * np.random.sample()), int(w * np.random.sample())
        depth[y, x] = 6.0 * np.random.sample()

    t1 = time.time()
    samples, vec = createSamples(depth, perc_samples)
    interpolated = getVoronoi(depth.shape, samples, vec)
    t2 = time.time()
    print('Time to create samples and get Voronoi: ' + str(t2 - t1))

    figsize = (6, 2.5)
    plt.figure(figsize = figsize)

    plt.subplot(1, 2, 1)
    plt.title('Original')
    plt.imshow(depth, cmap='plasma')
    plt.colorbar(fraction = 0.046, pad = 0.04)
    
    plt.subplot(1, 2, 2)
    plt.title('Natural Neighbor')
    plt.imshow(interpolated, cmap='plasma')
    plt.colorbar(fraction = 0.046, pad = 0.04)

    # plt.figure()
    # x = range(h*w)
    # flat = interpolated.copy()
    # flat[1::2] = interpolated[1::2,::-1]
    # flat = flat.ravel()
    # plt.plot(x[0:w], flat[0:w])

    plt.subplots_adjust(wspace = 0.3)
    plt.show()

if __name__ == "__main__":
    main()