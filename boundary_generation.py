# Filename: 'boundary_generation.py'
# Date: 07/11/2022
# Author: Connor Jordan
# Institution: University of Edinburgh (IIE)
# This script takes x, y, z data and tries to determine the boundary using alpha shapes.
# https://stackoverflow.com/questions/72418933/find-boundary-points-of-xy-coordinates
# https://stackoverflow.com/questions/50549128/boundary-enclosing-a-given-set-of-points
# https://gist.github.com/AndreLester/589ea1eddd3a28d00f3d7e47bd9f28fb

from datetime import datetime
import matplotlib.pyplot as plt
import numpy as np
import shapely.geometry as geometry
from shapely.ops import cascaded_union, polygonize
from scipy.spatial import Delaunay
import fiona
from sys import exit
import alphashape

plotting = False  # best not to plot for large data sets as a shapefile is generated and viewable via QGIS more easily
reduction = False  # add whether a reduction phase is required - use bounds_vis.py & QGIS to determine boundaries first
mode = 'alphashapes'  # choose 'alphashapes' or 'custom'

# Step 1: Load in data

starttime = datetime.now()  # calculating run times

print('Modules imported... (', datetime.now() - starttime, ')')

dt_string = starttime.strftime("%d/%m/%Y %H:%M:%S")
print("Simulation start: ", dt_string, '\n')

if reduction is True:
    data = np.load('bathymetry.npy')
    print('Bathymetry data loaded... (', datetime.now() - starttime, ')')
    print('Original number of points = ', len(data[:, 0]))
else:
    data = np.load('bathymetry_reduced.npy')

Coords = data[:, :-1]  # remove final column i.e. elevation data

print('Elevation data dropped... (', datetime.now() - starttime, ')')

if plotting is True:
    x, y = Coords[:, 0], Coords[:, 1]
else:
    x, y = 0, 0


# Step 2: Remove redundant data prior to boundary determination

if reduction is True:
    # Define rectangular (for simplicity) bounds (can enter more than one) to remove data from
    left = [489400, 490325, 492741, 489875, 489762, 491160, 490555, 494525]
    bottom = [6502383, 6501252, 6502346, 6503269, 6501898, 6502415, 6501020, 6501590]
    right = [491160, 494525, 494385, 490960, 490325, 491555, 492370, 494760]
    top = [6503269, 6502415, 6503055, 6503585, 6502383, 6502810, 6501252, 6502435]
    Coords_x = []
    Coords_y = []

    for coordinate in Coords:
        if right[0] >= coordinate[0] >= left[0] and top[0] >= coordinate[1] >= bottom[0]:
            pass
        elif right[1] >= coordinate[0] >= left[1] and top[1] >= coordinate[1] >= bottom[1]:
            pass
        elif right[2] >= coordinate[0] >= left[2] and top[2] >= coordinate[1] >= bottom[2]:
            pass
        elif right[3] >= coordinate[0] >= left[3] and top[3] >= coordinate[1] >= bottom[3]:
            pass
        elif right[4] >= coordinate[0] >= left[4] and top[4] >= coordinate[1] >= bottom[4]:
            pass
        elif right[5] >= coordinate[0] >= left[5] and top[5] >= coordinate[1] >= bottom[5]:
            pass
        elif right[6] >= coordinate[0] >= left[6] and top[6] >= coordinate[1] >= bottom[6]:
            pass
        elif right[7] >= coordinate[0] >= left[7] and top[7] >= coordinate[1] >= bottom[7]:
            pass
        else:
            Coords_x.append(coordinate[0])
            Coords_y.append(coordinate[1])
    Coords_ = np.array([Coords_x, Coords_y]).T
    np.save('bathymetry_reduced.npy', Coords_)
    print('Redundant data removed... (', datetime.now() - starttime, ')')
    print('Reduced number of points = ', len(Coords_x))
    if plotting is True:
        x_, y_ = Coords_[:, 0], Coords_[:, 1]
        plt.plot(x, y, 'o', color='black', markersize=4)
        plt.plot(x_, y_, 'x', color='red', markersize=4)
        plt.show()


# Step 3: Determine boundary

t1 = datetime.now()


def alpha_shape(points, alpha):
    """
    Compute the alpha shape (concave hull) of a set of points.
    points: Iterable container of points.
    alpha: alpha value to influence the gooeyness of the border.
    Smaller numbers on't fall inward as much as larger numbers.
    Too large, and you lose everything!
    """
    if len(points) < 4:
        # When you have a triangle, there is no sense
        # in computing an alpha shape.
        return geometry.MultiPoint(list(points)).convex_hull

    # coords = np.array([point.coords[0] for point in points])
    # tri = Delaunay(coords)
    tri = Delaunay(points)
    triangles = points[tri.vertices]
    a = ((triangles[:, 0, 0] - triangles[:, 1, 0]) ** 2 + (triangles[:, 0, 1] - triangles[:, 1, 1]) ** 2) ** 0.5
    b = ((triangles[:, 1, 0] - triangles[:, 2, 0]) ** 2 + (triangles[:, 1, 1] - triangles[:, 2, 1]) ** 2) ** 0.5
    c = ((triangles[:, 2, 0] - triangles[:, 0, 0]) ** 2 + (triangles[:, 2, 1] - triangles[:, 0, 1]) ** 2) ** 0.5
    s = (a + b + c) / 2.0
    areas = (s*(s-a)*(s-b)*(s-c)) ** 0.5
    circums = a * b * c / (4.0 * areas)
    filtered = triangles[circums < (1.0 / alpha)]
    edge1 = filtered[:, (0, 1)]
    edge2 = filtered[:, (1, 2)]
    edge3 = filtered[:, (2, 0)]
    edge_points = np.unique(np.concatenate((edge1, edge2, edge3)), axis=0).tolist()
    m = geometry.MultiLineString(edge_points)
    triangles = list(polygonize(m))
    return cascaded_union(triangles), edge_points


print('Generating boundary... (', datetime.now() - starttime, ')')

if mode == 'custom':
    Boundary, edgepoints = alpha_shape(data, alpha=1)
elif mode == 'alphashapes':
    Boundary = alphashape.alphashape(data, alpha=0.15)
else:
    Boundary = 0
    print('Choose a mode!')
    exit(0)

print('Boundary generated... (', datetime.now() - starttime, ')')

t2 = datetime.now()

# Step 4: Write shapefile to act ask mask to clip interpolated data

print('Writing polygon shapefile... (', datetime.now() - starttime, ')')

# Define a polygon feature geometry with one attribute
schema = {'geometry': 'Polygon', 'properties': {'id': 'int'}}

# Write a new Shapefile
with fiona.open('boundary.shp', 'w', 'ESRI Shapefile', schema, crs='epsg:32630') as output:
    output.write({'geometry': geometry.mapping(Boundary), 'properties': {'id': 0}})

simulationtime = datetime.now() - starttime  # calculate simulation time

print('Shapefile written, total conversion process time = ', simulationtime)

print('Boundary generation time for custom alpha shapes algorithm:', t2-t1, 's')
