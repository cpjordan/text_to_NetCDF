# text_to_NetCDF
Interpolation of unstructured xyz data (e.g. bathymetry) in .txt or .csv format to a structured grid. in .nc format. Subsequent generation of boundary (concave hull - alphashapes) to create a mask for clipping resultant gridded data.  

1. Run 'txt_to_npy.py' - requires input file.
2. Run 'npy_to_nc_UTM.py' - requires input file and choice of interpolation method, resolution and espg (keep to UTM and change to WGS84 via QGIS).
3. If non-rectangular boundaries required, run the boundary generation file to generate a more precise outline. use the 'test_files/bounds_vis.py' to visualise the shapefiles over the gridded data to help reduce the number of data points if using a large data set.

Written originally for a very large data set of 100m+ points where the resolution was being reduced and hence nearest neighbour interpolation used.
