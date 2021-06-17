# -*- coding: utf-8 -*-

""" Module summary description.

More detailed description.
"""
import os
import uuid
from tempfile import gettempdir

from pyrasta.io_ import ESRI_DRIVER
from pyrasta.io_.files import ShapeTempFile, _copy_to_file, NamedTempFile

import gdal


def _raster_mask(raster, geodataframe, all_touched):
    """ Apply mask into raster

    Parameters
    ----------
    raster
    geodataframe
    all_touched

    Returns
    -------

    """

    with ShapeTempFile() as shp_file, \
            NamedTempFile(raster._gdal_driver.GetMetadata()['DMD_EXTENSION']) as out_file:

        _copy_to_file(raster, out_file.path)
        geodataframe.to_file(shp_file.path, driver=ESRI_DRIVER)
        out_ds = gdal.Open(out_file.path, 1)
        gdal.Rasterize(out_ds,
                       shp_file.path,
                       bands=[bd + 1 for bd in range(raster.nb_band)],
                       burnValues=[raster.no_data],
                       allTouched=all_touched)

    out_ds = None

    return raster.__class__(out_file.path)
