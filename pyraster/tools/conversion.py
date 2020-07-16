# -*- coding: utf-8 -*-

""" Module summary description.

More detailed description.
"""
import gdal

from pyraster.crs import srs_from
from pyraster.io import RasterTempFile
from pyraster.tools import set_no_data


def _padding(raster, pad_x, pad_y, pad_value):
    """ Add pad values around raster

    Description
    -----------

    Parameters
    ----------
    raster: RasterBase
        raster to pad
    pad_x: int
        x padding size (new width will therefore be RasterXSize + 2 * pad_x)
    pad_y: int
        y padding size (new height will therefore be RasterYSize + 2 * pad_y)
    pad_value: int or float
        value to set to pad area around raster

    Returns
    -------
    """

    with RasterTempFile() as out_file:
        out_ds = raster._gdal_driver.Create(out_file, raster.x_size + 2 * pad_x, raster.y_size + 2 * pad_y,
                                            raster.nb_band, raster._gdal_dataset.GetRasterBand(1).DataType)
    out_ds.SetGeoTransform((raster.x_origin - pad_x * raster.resolution[0], raster.resolution[0],
                            0, raster.y_origin + pad_y * raster.resolution[1], 0, -raster.resolution[1]))
    out_ds.SetProjection(raster._gdal_dataset.GetProjection())
    set_no_data(out_ds, raster.no_data)

    for band in range(1, raster.nb_band + 1):
        out_ds.GetRasterBand(band).Fill(pad_value)
        gdal.Warp(out_ds, raster._gdal_dataset)

    # Close dataset
    out_ds = None

    return out_file


def _project_raster(raster, new_crs):
    """ Project raster onto new CRS

    """
    with RasterTempFile() as out_file:
        gdal.Warp(out_file, raster._gdal_dataset, dstSRS=srs_from(new_crs))


def _resample_raster(raster, factor):
    """ Resample raster

    Parameters
    ----------
    raster: RasterBase
        raster to resample
    factor: int or float
        Resampling factor
    """
    with RasterTempFile() as out_file:
        out_ds = raster._gdal_driver.Create(out_file, raster.x_size * factor, raster.y_size * factor, raster.nb_band,
                                            raster._gdal_dataset.GetRasterBand(1).DataType)
    out_ds.SetGeoTransform((raster.x_origin, raster.resolution[0] / factor, 0, raster.y_origin, 0,
                            -raster.resolution[1] / factor))
    out_ds.SetProjection(raster._gdal_dataset.GetProjection())
    set_no_data(out_ds, raster.no_data)

    for band in range(1, raster.nb_band+1):
        gdal.RegenerateOverview(raster._gdal_dataset.GetRasterBand(band), out_ds.GetRasterBand(band), 'mode')

    # Close dataset
    out_ds = None

    return out_file
