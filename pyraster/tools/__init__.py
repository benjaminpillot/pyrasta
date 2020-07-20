# -*- coding: utf-8 -*-

""" Module summary description.

More detailed description.
"""

__author__ = 'Benjamin Pillot'
__copyright__ = 'Copyright 2020, Benjamin Pillot'
__email__ = 'benjaminpillot@riseup.net'

from functools import wraps

from pyraster.io import RasterTempFile


def _return_raster(function):
    @wraps(function)
    def return_raster(raster, *args, **kwargs):
        with RasterTempFile() as out_file:
            function(raster, out_file.path, *args, **kwargs)
            new_raster = raster.__class__(out_file.path)
            new_raster._temp_file = out_file

        return new_raster
    return return_raster


def _gdal_temp_dataset(out_file, raster, x_size, y_size, geo_transform, data_type, no_data):
    """ Create gdal temporary dataset

    """
    out_ds = raster._gdal_driver.Create(out_file, x_size, y_size, raster.nb_band, data_type)
    out_ds.SetGeoTransform(geo_transform)
    out_ds.SetProjection(raster._gdal_dataset.GetProjection())
    _set_no_data(out_ds, no_data)

    return out_ds


def _set_no_data(gdal_ds, no_data):
    """ Set no data value into gdal dataset

    Description
    -----------

    Parameters
    ----------
    gdal_ds: gdal.Dataset
        gdal dataset
    no_data: list or tuple
        list of no data values corresponding to each raster band

    """
    for band in range(gdal_ds.RasterCount):
        try:
            gdal_ds.GetRasterBand(band + 1).SetNoDataValue(no_data[band])
        except TypeError:
            pass
