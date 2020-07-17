# -*- coding: utf-8 -*-

""" Module summary description.

More detailed description.
"""

__author__ = 'Benjamin Pillot'
__copyright__ = 'Copyright 2020, Benjamin Pillot'
__email__ = 'benjaminpillot@riseup.net'

from pyraster.io import RasterTempFile


def _gdal_temp_dataset(raster, x_size, y_size, geo_transform, data_type=None, no_data=None):
    """ Create gdal temporary dataset

    """
    if no_data is None:
        no_data = raster.no_data

    if data_type is None:
        data_type = raster._gdal_dataset.GetRasterBand(1).DataType

    with RasterTempFile() as out_file:
        out_ds = raster._gdal_driver.Create(out_file, x_size, y_size, raster.nb_band, data_type)
    out_ds.SetGeoTransform(geo_transform)
    out_ds.SetProjection(raster._gdal_dataset.GetProjection())
    _set_no_data(out_ds, no_data)

    return out_ds, out_file


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
