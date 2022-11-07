# Filename: 'npy_to_nc_tester.py'
# Date: 18/10/2022
# Author: Connor Jordan
# Institution: University of Edinburgh (IIE)
# This script converts an .npy array of format UTM x-coordinate, UTM y-coordinate, elevation into a NetCDF of format
# latitude, longitude, elevation.
# https://towardsdatascience.com/create-netcdf-files-with-python-1d86829127dd

import numpy as np
from scipy.interpolate import griddata
import netCDF4 as nc
from datetime import datetime
import pyproj

starttime = datetime.now()  # calculating run times

dt_string = starttime.strftime("%d/%m/%Y %H:%M:%S")
print("Simulation start: ", dt_string, '\n')

crs = pyproj.CRS.from_epsg(4326)
transformer = pyproj.Transformer.from_crs("EPSG:32630", "EPSG:4326", always_xy=True)

print('Modules imported... (', datetime.now() - starttime, ')')

data = np.load('bathymetry.npy')

print('Bathymetry data loaded... (', datetime.now() - starttime, ')')

X_UTM = data[:, 0]
Y_UTM = data[:, 1]
Elevation = data[:, 2]

# Assign NaN (Not a Number) to land points (invalid points) -  prevents errors from occurring but does not impact
# interpolation
elev_list = np.where(Elevation <= 0, np.nan, Elevation)

print('Data sliced... (', datetime.now() - starttime, ')')

min_X_UTM, max_X_UTM, min_Y_UTM, max_Y_UTM = min(X_UTM), max(X_UTM), min(Y_UTM), max(Y_UTM)

resolution = 2  # desired resolution in m
x_number = int(np.ceil(np.abs(max_X_UTM-min_X_UTM) / resolution))
y_number = int(np.ceil(np.abs(max_Y_UTM-min_Y_UTM) / resolution))

print('Grid point interval determined... (', datetime.now() - starttime, ')')

print('Number of interpolated points:', x_number*y_number)

lon, lat = transformer.transform(X_UTM, Y_UTM)

print('Coordinates converted to lat/long... (', datetime.now() - starttime, ')')

min_lon, max_lon, min_lat, max_lat = min(lon), max(lon), min(lat), max(lat)

# x_res = np.abs(max_lon-min_lon) / x_number  # grid x resolution (in degrees)
# y_res = np.abs(max_lat-min_lat) / y_number  # grid y resolution (in degrees)

# xi = np.arange(min_lon, max_lon+x_res, x_res)  # Set up grid x coordinates
# yi = np.arange(min_lat, max_lat+y_res, y_res)  # Set up grid y coordinates

xi = np.linspace(min_lon, max_lon, x_number)  # Set up grid x coordinates
yi = np.linspace(min_lat, max_lat, y_number)  # Set up grid y coordinates

print('Grid coordinates set up... (', datetime.now() - starttime, ')')

xx, yy = np.meshgrid(xi, yi, indexing='ij')  # Create grid of values, xx is grid of x values and likewise for yy

print('Grid meshed... (', datetime.now() - starttime, ')')

# Interpolate velocity and direction fields from coordinates (x,y) to grid (xx, yy)
elev_grid = griddata((lon, lat), elev_list, (xx, yy), method='nearest')

elev_grid_ = np.transpose(elev_grid)

print('Data interpolated to grid... (', datetime.now() - starttime, ')')

print('\nConverting to NetCDF... (', datetime.now() - starttime, ')')

# Take crs from https://epsg.io/3857
ds = nc.Dataset('bathymetry.nc', 'w', 'NETCDF4') # using netCDF4 for output format

lon = ds.createDimension('lon', xi.size)
lat = ds.createDimension('lat', yi.size)

crs = ds.createVariable("WGS84", 'c')
crs.spatial_ref = 'GEOGCS["GCS_WGS_1984", DATUM["D_WGS_1984", SPHEROID["WGS_1984",6378137.0,298.257223563]],' +\
                  'PRIMEM["Greenwich",0.0], UNIT["Degree",0.0174532925199433]]'

lons = ds.createVariable('lon', 'f4', ('lon',))
lats = ds.createVariable('lat', 'f4', ('lat',))
elev = ds.createVariable('elev', 'f4', ('lat', 'lon',))
elev.units = "meters"
elev.positive = "down"
elev.coordinates = "lat lon"
elev.grid_mapping = 'WGS84'
elev.grid_mapping_name = "latitude_longitude"

lons.long_name = "longitude"
lons.standard_name = "longitude"
lons.units = "degrees_east"
#lons.grid_mapping = "crs"
lons.grid_mapping = "WGS84"
lons.grid_mapping_name = "latitude_longitude"
# lons.valid_min = min(xi)
# lons.valid_max = max(xi)
lons.actual_range = (min(xi), max(xi))
lons[:] = xi

lats.long_name = "latitude"
lats.standard_name = "latitude"
lats.units = "degrees_north"
#lats.grid_mapping = "crs"
lats.grid_mapping = "WGS84"
lats.grid_mapping_name = "latitude_longitude"
lats.actual_range = (min(yi), max(yi))
lats[:] = yi

elev[:, :] = elev_grid_

print(elev_grid_.shape)

ds.close()

simulationtime = datetime.now() - starttime  # calculate simulation time

print('NetCDF written, total conversion process time = ', simulationtime)

