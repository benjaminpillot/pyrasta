# -*- coding: utf-8 -*-

""" Module summary description.

More detailed description.
"""

import rasterio

from pyraster.tools.merge import _rasterio_merge_modified

r1 = rasterio.open("/pyraster/tests/raster_1.tif")
r2 = rasterio.open("/pyraster/tests/raster_2.tif")
sources = [r1, r2]
out_file = "/pyraster/tests/test_merge.tif"
_rasterio_merge_modified(sources, out_file)
