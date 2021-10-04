# -*- coding: utf-8 -*-

""" Module summary description.

More detailed description.
"""

from functools import wraps

from pyrasta import GDAL_DEFAULT_DRIVER
from pyrasta.io_.files import RasterTempFile

try:
    from osgeo import gdal
except ImportError:
    import gdal


def driver_authorizes_creation(gdal_driver):

    return True if 'DCAP_CREATE' in gdal_driver.GetMetadata().keys() else False


def _return_raster(function):
    @wraps(function)
    def return_raster(raster, *args, **kwargs):
        try:
            if driver_authorizes_creation(raster._gdal_driver):
                gdal_driver = raster._gdal_driver
            else:
                gdal_driver = GDAL_DEFAULT_DRIVER
            with RasterTempFile(gdal_driver.GetMetadata()['DMD_EXTENSION']) as out_file:
                function(raster, out_file.path, *args, **kwargs)
                new_raster = raster.__class__(out_file.path)
        except AttributeError:
            gdal_driver = [arg for arg in args if isinstance(arg, gdal.Driver)][0]
            args = [arg for arg in args if not isinstance(arg, gdal.Driver)]
            with RasterTempFile(gdal_driver.GetMetadata()['DMD_EXTENSION']) as out_file:
                try:
                    function(raster, out_file.path, gdal_driver, *args, **kwargs)
                except TypeError:
                    function(raster, out_file.path, *args, **kwargs)
                new_raster = raster(out_file.path)
        finally:
            new_raster._temp_file = out_file

        return new_raster
    return return_raster


def _gdal_temp_dataset(out_file, gdal_driver, projection, x_size, y_size,
                       nb_band, geo_transform, data_type, no_data):
    """ Create gdal temporary dataset

    """
    try:
        out_ds = gdal_driver.Create(out_file, x_size, y_size, nb_band, data_type)
    except RuntimeError:
        out_ds = GDAL_DEFAULT_DRIVER.Create(out_file, x_size,
                                            y_size, nb_band, data_type)

    out_ds.SetGeoTransform(geo_transform)
    out_ds.SetProjection(projection)
    _set_no_data(out_ds, no_data)

    return out_ds


def _clone_gdal_dataset(raster, out_file, data_type=None):

    if data_type is None:
        data_type = raster.data_type

    return _gdal_temp_dataset(out_file,
                              raster._gdal_driver,
                              raster._gdal_dataset.GetProjection(),
                              raster.x_size,
                              raster.y_size,
                              raster.nb_band,
                              raster.geo_transform,
                              data_type,
                              raster.no_data)


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
            gdal_ds.GetRasterBand(band + 1).SetNoDataValue(no_data)
        except TypeError:
            pass
