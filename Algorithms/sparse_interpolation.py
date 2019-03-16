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
	"""
    Using perc_samples, return random number of samples from original data.
    Sparse identity matrices are used to conserve memory since identity
    matrices are mostly zeros.
    """
	height = depth.shape[0]
	width = depth.shape[1]
	N = height * width
	K = int(N * perc_samples)

	xGT = depth.flatten()
	rand = np.random.permutation(N)[:K]
	a = np.isnan(xGT[rand])
	samples = rand[np.nonzero(~a)[0]]

	Rfull = sparse.eye(N)
	R = Rfull.tocsr()[samples,:]
	measured_vector = R*xGT

	return samples, measured_vector

def interpolateDepthImage(shape, samples, measured_vector):
	"""
    Using just the original shape of depth image and random samples chosen,
    return a newly constructed depth image by interpolating known points.
    In this case use radial basis function after testing.
    """
	h = np.arange(0, shape[0])
	w = np.arange(0, shape[1])

	Yq, Zq = np.meshgrid(w, h)
	Y_sample = Yq.flatten()[samples]
	Z_sample = Zq.flatten()[samples]

	rbf1 = Rbf(Y_sample, Z_sample, measured_vector, function='linear')
	interpolated = rbf1(Yq, Zq)

	return interpolated

def main():
	h = 6
	w = 9

	depth = np.zeros((h, w))
	depth.fill(np.nan)
	for _ in range(int((h * w) / 3)):
		y, x = int(h * np.random.sample()), int(w * np.random.sample())
		depth[y, x] = 4.0 * np.random.sample()

	t1 = time.time()
	samples, measured = createSamples(depth, 1)
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






