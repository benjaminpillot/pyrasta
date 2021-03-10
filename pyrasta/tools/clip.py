# -*- coding: utf-8 -*-

""" Module summary description.

More detailed description.
"""
from pyrasta.io_.files import RasterTempFile

import gdal

from pyrasta.tools import _return_raster


@_return_raster
def _clip_raster_by_extent(raster, out_file, bounds):

    gdal.Warp(out_file,
              raster._gdal_dataset,
              outputBounds=bounds,
              srcNodata=raster.no_data,
              dstNodata=raster.no_data,
              outputType=raster.data_type)
