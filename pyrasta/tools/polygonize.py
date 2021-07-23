# -*- coding: utf-8 -*-

""" Module summary description.

More detailed description.
"""
import math

import gdal
import ogr
from pyrasta.crs import srs_from
from pyrasta.tools.mapping import GDAL_TO_OGR
from pyrasta.utils import gdal_progress_bar


def _polygonize(raster, filename, band, layer_name,
                field_name, ogr_driver, is_8_connected,
                progress_bar):
    """

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
    dst_layer = dst_ds.CreateLayer(layer_name, srs_from(raster.crs))

    field_def = ogr.FieldDefn(field_name, GDAL_TO_OGR[raster.data_type])
    dst_layer.CreateField(field_def)

    callback, callback_data = gdal_progress_bar(progress_bar,
                                                description="Polygonize raster")

    gdal.Polygonize(raster._gdal_dataset.GetRasterBand(band),
                    None,
                    dst_layer,
                    0,
                    [connectivity],
                    callback=callback,
                    callback_data=callback_data)

    return 0