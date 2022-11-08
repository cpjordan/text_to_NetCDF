# Filename: 'bounds_vis.py'
# Date: 07/11/2022
# Author: Thanasis Angeloudis, edited by Connor Jordan
# Institution: University of Edinburgh (IIE)
# This script generates rectangular Polygon shapefiles.

import shapely.geometry
import numpy as np
import fiona.crs
import pyproj

'''
Shapefile requirements

A coordinate reference system is required in order to create the shapefile. The pyproj here defines a coordinate system 
to be used which is WGS 84 / UTM zone 30. This uses the WGS 84 geographic 2D CRS (coordinate reference system) as its 
base CRS and the UTM zone 30N (Transverse Mercator) as its projection. fiona then converts from PROJ.4 string to a 
mapping of parameters for use with fiona.collection. 
schema is the dictionary containing the geometry and properties in the form of Lines and the Physical ID associated 
with each line.
'''
UTM_ZONE30 = pyproj.Proj(proj='utm', zone=30, datum='WGS84', units='m', errcheck=True)
schema = {'geometry': 'Polygon', 'properties': {'PhysID': 'int'}}
crs = fiona.crs.from_string(UTM_ZONE30.srs)

left = [489400, 490325, 492741, 489875, 489762, 491160, 490555, 494525]
bottom = [6502383, 6501252, 6502346, 6503269, 6501898, 6502415, 6501020, 6501590]
right = [491160, 494525, 494385, 490960, 490325, 491555, 492370, 494760]
top = [6503269, 6502415, 6503055, 6503585, 6502383, 6502810, 6501252, 6502435]

with fiona.collection("reductionbounds.shp", "w", "ESRI Shapefile", schema, crs=crs) as output:
    for i in np.arange(0, len(left)):
        output.write({'geometry': shapely.geometry.mapping(shapely.geometry.Polygon([(left[i], bottom[i]),
                                                                                     (left[i], top[i]),
                                                                                     (right[i], top[i]),
                                                                                     (right[i], bottom[i])])),
                      'properties': {'PhysID': 0}})
