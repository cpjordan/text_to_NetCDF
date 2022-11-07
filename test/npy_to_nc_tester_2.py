# Filename: 'npy_to_nc_tester_2.py'
# Date: 18/10/2022
# Author: Connor Jordan
# Institution: University of Edinburgh (IIE)
# This script converts an .npy array of format UTM x-coordinate, UTM y-coordinate, elevation.
# https://towardsdatascience.com/create-netcdf-files-with-python-1d86829127dd

import numpy as np
from scipy.interpolate import griddata, RBFInterpolator
import netCDF4 as nc
from datetime import datetime
import matplotlib.pyplot as plt
import pyproj
from sys import exit

crs = pyproj.CRS.from_epsg(4326)
transformer = pyproj.Transformer.from_crs("EPSG:32630", "EPSG:4326", always_xy=True)

print('Modules imported...')

data = np.loadtxt('tester.txt', delimiter=",", skiprows=1)  # output: n times 1 array of tuples

print('Elevation data loaded...')

X_UTM = data[:, 0]
Y_UTM = data[:, 1]
Elevation = data[:, 2]

lon, lat = transformer.transform(X_UTM, Y_UTM)

starttime = datetime.now()  # to calculate script runtime

# -----------

# Assign NaN (Not a Number) to land points (invalid points) -  prevents errors from occurring but does not
# impact interpolation
elev_list = np.array([n if n != 0. else np.nan for n in Elevation])

# The output lists may be very long (depending on mesh fineness and domain size), however in FLORIS the
# velocities are interpolated and unless the flow field behaviour is complex then such large arrays of data are
# not required, therefore smaller lists can be created using a grid. (remember with linear spacing 100 is the
# number of points)
min_lon, max_lon, min_lat, max_lat = min(lon), max(lon), min(lat), max(lat)

x_res = np.abs(max_lon-min_lon) / 3
y_res = np.abs(max_lat-min_lat) / 5

xi = np.arange(min_lon, max_lon+x_res, x_res)  # Set up grid x coordinates
yi = np.arange(min_lat, max_lat+y_res, y_res)  # Set up grid y coordinates

xx, yy = np.meshgrid(xi, yi, indexing='ij')  # Create grid of values, xx is grid of x values and likewise for yy

# Interpolate velocity and direction fields from coordinates (x,y) to grid (xx, yy)
time0 = datetime.now()

elev_grid = griddata((lon, lat), elev_list, (xx, yy), method='cubic')

time1 = datetime.now() - time0

# print(xx)
# print(yy)
print(elev_grid)

# ig = plt.figure(figsize=(15,10),dpi=400)
# ax = plt.axes(projection='3d')
#
# ax.plot_surface(xx, yy, elev_grid, cmap='viridis', edgecolor='none')
# ax.invert_xaxis()
# ax.set_title('Surface plot')
# plt.show()

time2 = datetime.now()
scattered_points = np.stack([lon.ravel(), lat.ravel()],-1)
dense_points = np.stack([xx.ravel(), yy.ravel()], -1)
interpolation = RBFInterpolator(scattered_points, elev_list, neighbors=25, kernel='thin_plate_spline')
z_dense = interpolation(dense_points).reshape(xx.shape)
time3 = starttime.now() - time2
print(z_dense)

# ig = plt.figure(figsize=(15,10),dpi=400)
# ax = plt.axes(projection='3d')

# ax.plot_surface(xx, yy, z_dense, cmap='viridis', edgecolor='none')
# ax.invert_xaxis()
# ax.set_title('Surface plot')
# plt.show()

time2 = datetime.now()

# coordinates: array of shape (24rows, 2columns) - first column x value, second column y value
xobs = np.array([lon, lat]).T
# data points: list of 100 points
yobs = elev_list

# two meshes with rows/columns respectively ranging from -1 -> 1 in 24 increments (2arrays, 24rows, 24columns)
xgrid = np.mgrid[min_lon:max_lon:4j, min_lat:max_lat:6j]
# reshaped array of (24^2 row, 2columns i.e. 576rows, 2columns) -  first column x value, second column y value
xflat = xgrid.reshape(2, -1).T
# list of 576 interpolated data points (576,)
# xobs = (24,2), yobs = (24,), xflat = (576, 2)
yflat = RBFInterpolator(xobs, yobs)(xflat)
# 24 x 24 array reshaped to match the grid (24, 24)
ygrid = yflat.reshape(4, 6)

print(ygrid)

time3 = starttime.now() - time2

print(time1, time3)

print('Data interpolated...')

print('\nConverting to NetCDF...')

ds = nc.Dataset('test2.nc', 'w', 'NETCDF4') # using netCDF4 for output format

time = ds.createDimension('time', None)
lon = ds.createDimension('lon', xi.size)
lat = ds.createDimension('lat', yi.size)

lons = ds.createVariable('lon', 'f4', ('lon',))
lats = ds.createVariable('lat', 'f4', ('lat',))
elev = ds.createVariable('elev', 'f4', ('time', 'lat', 'lon',))
elev.units = 'm'

lons[:] = xi
lons.long_name = 'longitude'
lons.standard_name = 'longitude'
lons.units = 'degrees_east'
lons.grid_mapping = 'crs'
lons.grid_mapping_name = 'latitude_longitude'
# lons.valid_min = min(xi)
# lons.valid_max = max(xi)
lons.actual_range = (min(xi), max(xi))

print('Longitude range: ', lons.actual_range)

lats[:] = yi
lats.long_name = 'latitude'
lats.standard_name = 'latitude'
lats.units = 'degrees_north'
lats.actual_range = (min(yi), max(yi))

print('elev size before adding data', elev.shape)

elev[0, :, :] = ygrid

print('elev size after adding data', elev.shape)

ds.close()

simulationtime = datetime.now() - starttime  # calculate simulation time

print('NetCDF written, conversion process time = ', simulationtime)

