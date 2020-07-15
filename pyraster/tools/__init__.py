# -*- coding: utf-8 -*-

""" Module summary description.

More detailed description.
"""

__author__ = 'Benjamin Pillot'
__copyright__ = 'Copyright 2020, Benjamin Pillot'
__email__ = 'benjaminpillot@riseup.net'


def set_no_data(gdal_ds, no_data):
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
