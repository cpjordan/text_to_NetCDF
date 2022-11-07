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

print('Modules imported... (', datetime.now() - starttime, ')')

dt_string = starttime.strftime("%d/%m/%Y %H:%M:%S")
print("Simulation start: ", dt_string, '\n')

data = np.loadtxt('tester.txt', delimiter=",", skiprows=1)

print('Bathymetry data loaded... (', datetime.now() - starttime, ')')

X_UTM = data[:, 0]
Y_UTM = data[:, 1]
Elevation = data[:, 2]

# Assign NaN (Not a Number) to land points (invalid points) -  prevents errors from occurring but does not
# impact interpolation
elev_list = np.where(Elevation <= 0, np.nan, Elevation)

print('Data sliced... (', datetime.now() - starttime, ')')

min_X_UTM, max_X_UTM, min_Y_UTM, max_Y_UTM = min(X_UTM), max(X_UTM), min(Y_UTM), max(Y_UTM)

resolution = 0.5  # desired resolution in m

x_number = np.abs(max_X_UTM-min_X_UTM) / resolution
y_number = np.abs(max_Y_UTM-min_Y_UTM) / resolution

print('Number of interpolated points:', x_number*y_number)

xi = np.arange(min_X_UTM, max_X_UTM+resolution, resolution)  # Set up grid x coordinates
yi = np.arange(min_Y_UTM, max_Y_UTM+resolution, resolution)  # Set up grid y coordinates

print('Grid coordinates set up... (', datetime.now() - starttime, ')')

xx, yy = np.meshgrid(xi, yi, indexing='ij')  # Create grid of values, xx is grid of x values and likewise for yy

print('Grid meshed... (', datetime.now() - starttime, ')')

# Interpolate velocity and direction fields from coordinates (x,y) to grid (xx, yy)
elev_grid = griddata((X_UTM, Y_UTM), elev_list, (xx, yy), method='nearest')

elev_grid_ = np.transpose(elev_grid)

print('Data interpolated to grid... (', datetime.now() - starttime, ')')

print('\nConverting to NetCDF... (', datetime.now() - starttime, ')')

ds = nc.Dataset('test.nc', 'w', 'NETCDF4')  # using netCDF4 for output format

x = ds.createDimension('x', xi.size)
y = ds.createDimension('y', yi.size)

xs = ds.createVariable('x', 'f4', ('x',))
ys = ds.createVariable('y', 'f4', ('y',))
elev = ds.createVariable('elev', 'f4', ('y', 'x',))

crs = ds.createVariable("WGS_1984_UTM_Zone_30N", 'c')
crs.spatial_ref = 'PROJCS["WGS_1984_UTM_Zone_30N", GEOGCS["GCS_WGS_1984", DATUM["D_WGS_1984",' +\
                  'SPHEROID["WGS_1984",6378137.0,298.257223563]], PRIMEM["Greenwich",0.0],' +\
                  'UNIT["Degree",0.0174532925199433]], PROJECTION["Transverse_Mercator"],' +\
                  'PARAMETER["False_Easting",500000.0], PARAMETER["False_Northing",0.0],' +\
                  'PARAMETER["Central_Meridian",-3.0], PARAMETER["Scale_Factor",0.9996],' +\
                  'PARAMETER["Latitude_Of_Origin",0.0], UNIT["Meter",1.0]]'

xs[:] = xi
xs.long_name = 'Easting'
xs.standard_name = 'projection_x_coordinate'
xs.units = 'm'
xs.grid_mapping = 'WGS_1984_UTM_Zone_30N'
xs.grid_mapping_name = 'Northing Easting'
xs.actual_range = (min(xi), max(xi))

ys[:] = yi
ys.long_name = 'Northing'
ys.standard_name = 'projection_y_coordinate'
ys.units = 'm'
ys.grid_mapping = 'WGS_1984_UTM_Zone_30N'
ys.grid_mapping_name = 'Northing Easting'
ys.actual_range = (min(yi), max(yi))

elev.units = 'm'
elev.positive = "down"
elev.grid_mapping = 'WGS_1984_UTM_Zone_30N'
elev[:, :] = elev_grid_

ds.close()

simulationtime = datetime.now() - starttime  # calculate simulation time

print('NetCDF written, total conversion process time = ', simulationtime)
