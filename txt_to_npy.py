# Filename: 'txt_to_npy.py'
# Date: 17/10/2022
# Author: Connor Jordan
# Institution: University of Edinburgh (IIE)
# This script extracts elevation data from a .txt file and converts to an .npy file.

import numpy as np
from datetime import datetime

starttime = datetime.now()  # to calculate script runtime

# This loads ASCII (character encoding standard for electronic communication, ASCII codes represent text in
# computers) data stored in a delimited text file (.txt). The shape of the output is (n, 1) where n = no. of lines
# because each line of data is represented as a tuple, so there are n lines of tuples. Skip first row i.e. headers.
data = np.loadtxt('3475 Stroma AllData WGS84.txt', delimiter=",", skiprows=1)  # output: n times 1 array of tuples

simulationtime = datetime.now() - starttime  # calculate simulation time

print('Unpacking time = ', simulationtime)

np.save('bathymetry.npy', data)

print(data)
