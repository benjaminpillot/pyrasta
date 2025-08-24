# -*- coding: utf-8 -*-

""" Module summary description.

More detailed description.
"""
from functools import partial


def _mask(arrays, no_data):
    src = arrays[0]
    mask = arrays[1]
    src[mask == 1] = no_data

    return src


def _reversed_mask(arrays, no_data):
    src = arrays[0]
    mask = arrays[1]
    src[mask != 1] = no_data

    return src


def _raster_mask(raster, geodataframe, reverse,
                 driver, output_type, no_data, all_touched,
                 window_size):
    """ Apply mask into raster

    """
    mask = raster.__class__.rasterize(geodataframe,
                                      # raster.crs.to_wkt(),
                                      raster.x_size,
                                      raster.y_size,
                                      raster.geo_transform,
                                      burn_values=[1],
                                      all_touched=all_touched)

    if reverse:
        mask_fcn = partial(_reversed_mask, no_data=no_data)
    else:
        mask_fcn = partial(_mask, no_data=no_data)

    return raster.__class__.raster_calculation([raster, mask],
                                               mask_fcn,
                                               gdal_driver=driver,
                                               output_type=output_type,
                                               no_data=no_data,
                                               description="Compute mask",
                                               window_size=window_size,
                                               nb_processes=1,
                                               chunksize=1)
