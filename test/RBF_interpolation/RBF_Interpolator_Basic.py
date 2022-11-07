import matplotlib.pyplot as plt
from scipy.interpolate import RBFInterpolator
from scipy.stats.qmc import Halton
import numpy as np

# object that will generate random numbers
rng = np.random.default_rng()
# coordinates: array of shape (100rows, 2columns) - first column x value, second column y value
xobs = 2*Halton(2, seed=rng).random(10) - 1
# data points: list of 100 points
yobs = np.sum(xobs, axis=1)*np.exp(-6*np.sum(xobs**2, axis=1))

# two meshes with rows/columns respectively ranging from -1 -> 1 in 50 increments (2arrays, 50rows, 50columns)
xgrid = np.mgrid[-1:1:50j, -1:1:50j]
# reshaped array of (50^2 row, 2columns i.e. 2500rows, 2columns) -  first column x value, second column y value
xflat = xgrid.reshape(2, -1).T
# list of 2500 interpolated data points (2500,)
# xobs = (100,2), yobs = (100,), xflat = (2500, 2)
yflat = RBFInterpolator(xobs, yobs)(xflat)
# 50 x 50 array reshaped to match the grid (50, 50)
ygrid = yflat.reshape(50, 50)

fig, ax = plt.subplots()
# *xobs = list of 2 entries of (50x50 arrays) - x & y coordinates, ygrid = 50x50 array of data points
ax.pcolormesh(*xgrid, ygrid, vmin=-0.25, vmax=0.25, shading='gouraud')
# xobs = (100rows, 2columns), *xobs = list of 100 entries of (2items [x,y])
# *xobs.T = list of 2 entries of [100items] (first entry = x values, second entry = y values)
p = ax.scatter(*xobs.T, c=yobs, s=50, ec='k', vmin=-0.25, vmax=0.25)
fig.colorbar(p)
plt.show()