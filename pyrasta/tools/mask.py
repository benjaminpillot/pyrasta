# -*- coding: utf-8 -*-

""" Module summary description.

More detailed description.
"""
from functools import partial

from pyrasta.io_ import ESRI_DRIVER
from pyrasta.io_.files import ShapeTempFile, _copy_to_file, NamedTempFile

import gdal


def _mask(arrays, no_data):
    src = arrays[0]
    mask = arrays[1]
    src[mask == 1] = no_data

    return src


def _raster_mask(raster, geodataframe, driver, output_type, no_data, all_touched,
                 window_size):
    """ Apply mask into raster

    """
    mask = raster.__class__.rasterize(geodataframe,
                                      raster.crs.to_wkt(),
                                      raster.x_size,
                                      raster.y_size,
                                      raster.geo_transform,
                                      burn_values=[1],
                                      all_touched=all_touched)

    return raster.__class__.raster_calculation([raster, mask],
                                               partial(_mask, no_data=no_data),
                                               gdal_driver=driver,
                                               output_type=raster.data_type,
                                               no_data=no_data,
                                               description="Compute mask",
                                               window_size=window_size,
                                               nb_processes=1,
                                               chunksize=1)


    # with ShapeTempFile() as shp_file, \
    #         NamedTempFile(raster._gdal_driver.GetMetadata()['DMD_EXTENSION']) as out_file:
    #
    #     _copy_to_file(raster, out_file.path)
    #     geodataframe.to_file(shp_file.path, driver=ESRI_DRIVER)
    #     out_ds = gdal.Open(out_file.path, 1)
    #     gdal.Rasterize(out_ds,
    #                    shp_file.path,
    #                    bands=[bd + 1 for bd in range(raster.nb_band)],
    #                    burnValues=[10],
    #                    allTouched=all_touched)
    #
    # out_ds = None

    # return raster.__class__(out_file.path)
    # new_raster = raster.__class__(out_file.path)
    # new_raster._temp_file = out_file

    # return new_raster
