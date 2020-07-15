# -*- coding: utf-8 -*-

""" Module summary description.

More detailed description.
"""

import rasterio

from pyraster.tools.merge import _rasterio_merge_modified

r1 = rasterio.open("/home/benjamin/Documents/pyraster/pyraster/test/raster_1.tif")
r2 = rasterio.open("/home/benjamin/Documents/pyraster/pyraster/test/raster_2.tif")
sources = [r1, r2]
out_file = "/home/benjamin/Documents/pyraster/pyraster/test/test_merge.tif"
_rasterio_merge_modified(sources, out_file)
