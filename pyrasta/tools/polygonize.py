# -*- coding: utf-8 -*-

""" Module summary description.

More detailed description.
"""
import math

import gdal
import ogr
from pyrasta.crs import srs_from
from pyrasta.utils import gdal_progress_bar


def _polygonize(raster, filename, band, layer_name,
                field_name, ogr_driver, is_8_connected,
                progress_bar):
    """ Polygonize raster

    Parameters
    ----------
    raster
    filename
    band
    layer_name
    field_name
    ogr_driver
    is_8_connected
    progress_bar

    Returns
    -------

    """
    connectivity = "8CONNECTED=%d" % (8 if is_8_connected else 4)
    dst_ds = ogr_driver.CreateDataSource(filename)
    dst_layer = dst_ds.CreateLayer(layer_name,
                                   geom_type=ogr.wkbPolygon,
                                   srs=srs_from(raster.crs))

    fd = ogr.FieldDefn(field_name, ogr.OFTInteger)
    dst_layer.CreateField(fd)

    callback, callback_data = gdal_progress_bar(progress_bar,
                                                description="Polygonize raster")

    srcband = raster._gdal_dataset.GetRasterBand(band)
    maskband = srcband.GetMaskBand()

    gdal.Polygonize(srcband,
                    maskband,
                    dst_layer,
                    0,
                    [connectivity],
                    callback=callback,
                    callback_data=callback_data)

    dst_ds = None

    return 0
