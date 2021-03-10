# -*- coding: utf-8 -*-

""" Module summary description.

More detailed description.
"""
import numpy as np
from matplotlib import pyplot

from pyrasta.raster import DigitalElevationModel
from pyrasta.tools.srtm import from_cgiar_online_database

# bounds = (5, 40, 10, 45)
# test = from_cgiar_online_database(bounds)
# test.to_file("/home/benjamin/srtm_corse.tif")

# test = DigitalElevationModel("/home/benjamin/dem_test.tif").clip((13, 42, 15, 45)).to_file(
#     "/home/benjamin/dem_clip_test.tif")
test = DigitalElevationModel("/home/benjamin/srtm_corse.tif")
print("%d,%d" % (test.x_size, test.y_size))
clip = test.read_array(bounds=(8, 42, 10, 44))
print(clip.shape)
clip[clip == -32768] = 0

pyplot.imshow(clip)
pyplot.show()
