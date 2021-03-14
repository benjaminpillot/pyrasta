# -*- coding: utf-8 -*-

""" Module summary description.

More detailed description.
"""
from pyrasta.io_ import ESRI_DRIVER
from pyrasta.io_.files import ShapeTempFile, RasterTempFile
from pyrasta.tools import _gdal_temp_dataset

import gdal


def _rasterize(raster_class, geodataframe, burn_values, attribute,
               gdal_driver, projection, x_size, y_size, nb_band,
               geo_transform, data_type, no_data, all_touched):
    """ Rasterize geographic layer

    Parameters
    ----------
    raster_class: RasterBase
        Raster class to return
    geodataframe: geopandas.GeoDataFrame or gistools.layer.GeoLayer
        Geographic layer to be rasterized
    burn_values: None or list[float] or list[int]
        list of values to burn in each band, excusive with attribute
    attribute: str
        attribute in layer from which burn value must be retrieved
    gdal_driver
    projection
    x_size: int
    y_size: int
    nb_band: int
    geo_transform: tuple
    data_type
    no_data
    all_touched: bool

    Returns
    -------

    """

    with ShapeTempFile() as shp_file, \
            RasterTempFile(gdal_driver.GetMetadata()['DMD_EXTENSION']) as out_file:

        geodataframe.to_file(shp_file.path, driver=ESRI_DRIVER)

        out_ds = _gdal_temp_dataset(out_file.path,
                                    gdal_driver,
                                    projection,
                                    x_size,
                                    y_size,
                                    nb_band,
                                    geo_transform,
                                    data_type,
                                    no_data)

        gdal.Rasterize(out_ds,
                       shp_file.path,
                       bands=[bd + 1 for bd in range(nb_band)],
                       burnValues=burn_values,
                       attribute=attribute,
                       allTouched=all_touched)

    out_ds = None

    # Be careful with the temp file, make a pointer to be sure
    # the Python garbage collector does not destroy it !
    raster = raster_class(out_file.path)
    raster._temp_file = out_file

    return raster
