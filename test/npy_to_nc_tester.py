# Filename: 'npy_to_nc_tester.py'
# Date: 18/10/2022
# Author: Connor Jordan
# Institution: University of Edinburgh (IIE)
# This script converts an .npy array of format UTM x-coordinate, UTM y-coordinate, elevation.
# https://towardsdatascience.com/create-netcdf-files-with-python-1d86829127dd

import numpy as np
from scipy.interpolate import griddata
import netCDF4 as nc
from datetime import datetime
import matplotlib.pyplot as plt
import pyproj
from sys import exit


crs = pyproj.CRS.from_epsg(4326)
transformer = pyproj.Transformer.from_crs("EPSG:32630","EPSG:4326", always_xy=True)

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
elev_grid = griddata((lon, lat), elev_list, (xx, yy), method='nearest')

print(xi)
print(yi)
print(elev_grid.shape)

fig = plt.figure()
ax1 = plt.contourf(xx, yy, elev_grid)
plt.show()

print('Data interpolated...')

print('\nConverting to NetCDF...')

# AT THIS POINT WE ARE SWITCHING TO WRITE MODE FOR NETCDF - ANYTHING WE WANT IN THE NETCDF FILE MUST GO HERE
ds = nc.Dataset('test.nc', 'w', 'NETCDF4')  # using netCDF4 for output format

time = ds.createDimension('time', None)
lon = ds.createDimension('lon', xi.size)
lat = ds.createDimension('lat', yi.size)

crs = ds.createVariable('crs', 'i4')
lons = ds.createVariable('lon', 'f4', ('lon',))
lats = ds.createVariable('lat', 'f4', ('lat',))
elev = ds.createVariable('elev', 'f4', ('time', 'lat', 'lon',))
elev.units = 'm'

crs.grid_mapping_name = 'crs'
crs.epsg_code = 'EPSG:4326'
crs.spatial_ref = """GEOGCS["WGS 84",DATUM["WGS_1984",SPHEROID["WGS 84",6378137,298.257223563,AUTHORITY["EPSG","7030"]],AUTHORITY["EPSG","6326"]],PRIMEM["Greenwich",0,AUTHORITY["EPSG","8901"]],UNIT["degree",0.01745329251994328,AUTHORITY["EPSG","9122"]],AUTHORITY["EPSG","4326"]]"""

lons[:] = xi
lons.long_name = 'longitude'
lons.standard_name = 'longitude'
lons.units = 'degrees_east'
lons.grid_mapping = 'WGS84'
lons.grid_mapping_name = 'latitude_longitude'
# lons.valid_min = min(xi)
# lons.valid_max = max(xi)
lons.actual_range = (min(xi), max(xi))

print('Longitude range: ', lons.actual_range)

lats[:] = yi
lats.long_name = 'latitude'
lats.standard_name = 'latitude'
lats.units = 'degrees_north'
lats.grid_mapping = 'WGS84'
lats.grid_mapping_name = 'latitude_longitude'
lats.actual_range = (min(yi), max(yi))

print('Latitude range: ', lats.actual_range)

print('elev size before adding data', elev.shape)

elev[0, :, :] = elev_grid

print('elev size after adding data', elev.shape)

ds.close()

simulationtime = datetime.now() - starttime  # calculate simulation time

print('NetCDF written, conversion process time = ', simulationtime)

