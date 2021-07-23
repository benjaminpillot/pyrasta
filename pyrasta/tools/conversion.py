# -*- coding: utf-8 -*-

""" Module summary description.

More detailed description.
"""
from pyrasta.crs import srs_from
from pyrasta.io_.files import VrtTempFile, _copy_to_file
from pyrasta.tools import _gdal_temp_dataset, _return_raster, _clone_gdal_dataset

# from osgeo import gdal_array

import affine
import gdal
from pyrasta.tools.mapping import NUMPY_TO_GDAL


@_return_raster
def _align_raster(in_raster, out_file, on_raster):
    """ Align raster on other raster

    """
    out_ds = _gdal_temp_dataset(out_file, in_raster._gdal_driver,
                                on_raster._gdal_dataset.GetProjection(),
                                on_raster.x_size, on_raster.y_size, in_raster.nb_band,
                                on_raster.geo_transform, in_raster.data_type, in_raster.no_data)

    gdal.Warp(out_ds, in_raster._gdal_dataset)

    # Close dataset
    out_ds = None


@_return_raster
def _array_to_raster(raster_class, out_file, gdal_driver,
                     array, crs, bounds, no_data):
    """ Convert array to (north up) raster

    Parameters
    ----------
    out_file:
    gdal_driver:
    array: numpy.ndarray
    crs: pyproj.CRS
    bounds: tuple
        Image boundaries as (xmin, ymin, xmax, ymax)
    no_data

    Returns
    -------

    """
    if array.ndim == 2:
        nb_band = 1
        x_size = array.shape[1]
        y_size = array.shape[0]
    else:
        nb_band = array.shape[0]
        x_size = array.shape[2]
        y_size = array.shape[1]

    xmin, ymin, xmax, ymax = bounds
    geo_transform = (xmin, (xmax - xmin)/x_size, 0,
                     ymax, 0, -(ymax - ymin)/y_size)

    out_ds = _gdal_temp_dataset(out_file,
                                gdal_driver,
                                crs.to_wkt(),
                                x_size,
                                y_size,
                                nb_band,
                                geo_transform,
                                NUMPY_TO_GDAL[array.dtype.name],
                                # gdal_array.NumericTypeCodeToGDALTypeCode(array.dtype),
                                no_data)

    if nb_band == 1:
        out_ds.GetRasterBand(nb_band).WriteArray(array)
    else:
        for band in range(nb_band):
            out_ds.GetRasterBand(band + 1).WriteArray(array[band, :, :])

    # Close dataset
    out_ds = None


@_return_raster
def _extract_bands(raster, out_file, bands):

    out_ds = gdal.Translate(out_file, raster._gdal_dataset, bandList=bands)

    # Close dataset
    out_ds = None


def _xy_to_2d_index(raster, x, y):
    """ Convert x/y map coordinates to 2d index

    """
    forward_transform = affine.Affine.from_gdal(*raster.geo_transform)
    reverse_transform = ~forward_transform
    px, py = reverse_transform * (x, y)

    return int(px), int(py)


@_return_raster
def _merge_bands(raster_class, out_file, sources, resolution, data_type, no_data):
    """ Merge multiple bands into one raster

    """
    vrt_ds = gdal.BuildVRT(VrtTempFile().path, [src._gdal_dataset for src in sources],
                           resolution=resolution, separate=True, VRTNodata=no_data)
    out_ds = gdal.Translate(out_file, vrt_ds, outputType=data_type)

    # Close dataset
    out_ds = None


@_return_raster
def _padding(raster, out_file, pad_x, pad_y, pad_value):
    """ Add pad values around raster

    Description
    -----------

    Parameters
    ----------
    raster: RasterBase
        raster to pad
    out_file: str
        output file to which to write new raster
    pad_x: int
        x padding size (new width will therefore be RasterXSize + 2 * pad_x)
    pad_y: int
        y padding size (new height will therefore be RasterYSize + 2 * pad_y)
    pad_value: int or float
        value to set to pad area around raster

    Returns
    -------
    """
    geo_transform = (raster.x_origin - pad_x * raster.resolution[0], raster.resolution[0], 0,
                     raster.y_origin + pad_y * raster.resolution[1], 0, -raster.resolution[1])
    out_ds = _gdal_temp_dataset(out_file,
                                raster._gdal_driver,
                                raster._gdal_dataset.GetProjection(),
                                raster.x_size + 2 * pad_x,
                                raster.y_size + 2 * pad_y,
                                raster.nb_band,
                                geo_transform,
                                raster.data_type,
                                raster.no_data)

    for band in range(1, raster.nb_band + 1):
        out_ds.GetRasterBand(band).Fill(pad_value)
        gdal.Warp(out_ds, raster._gdal_dataset)

    # Close dataset
    out_ds = None


@_return_raster
def _project_raster(raster, out_file, new_crs):
    """ Project raster onto new CRS

    """
    gdal.Warp(out_file, raster._gdal_dataset, dstSRS=srs_from(new_crs))


def _read_array(raster, band, bounds):
    """ Read array from raster

    """
    if bounds is None:
        return raster._gdal_dataset.ReadAsArray()
    else:
        x_min, y_min, x_max, y_max = bounds
        forward_transform = affine.Affine.from_gdal(*raster.geo_transform)
        reverse_transform = ~forward_transform
        px_min, py_max = reverse_transform * (x_min, y_min)
        px_max, py_min = reverse_transform * (x_max, y_max)
        x_size = int(px_max - px_min) + 1
        y_size = int(py_max - py_min) + 1

        if band is not None:
            return raster._gdal_dataset.GetRasterBand(band).ReadAsArray(int(px_min),
                                                                        int(py_min),
                                                                        x_size,
                                                                        y_size)
        else:
            return raster._gdal_dataset.ReadAsArray(int(px_min),
                                                    int(py_min),
                                                    x_size,
                                                    y_size)


def _read_value_at(raster, x, y):
    """ Read value at lat/lon map coordinates

    """
    forward_transform = affine.Affine.from_gdal(*raster.geo_transform)
    reverse_transform = ~forward_transform
    xoff, yoff = reverse_transform * (x, y)
    value = raster._gdal_dataset.ReadAsArray(xoff, yoff, 1, 1)
    if value.size > 1:
        return value
    else:
        return value[0, 0]


@_return_raster
def _resample_raster(raster, out_file, factor):
    """ Resample raster

    Parameters
    ----------
    raster: RasterBase
        raster to resample
    out_file: str
        output file to which to write new raster
    factor: int or float
        Resampling factor
    """
    geo_transform = (raster.x_origin, raster.resolution[0] / factor, 0,
                     raster.y_origin, 0, -raster.resolution[1] / factor)
    out_ds = _gdal_temp_dataset(out_file,
                                raster._gdal_driver,
                                raster._gdal_dataset.GetProjection(),
                                raster.x_size * factor,
                                raster.y_size * factor,
                                raster.nb_band,
                                geo_transform,
                                raster.data_type,
                                raster.no_data)

    for band in range(1, raster.nb_band+1):
        gdal.RegenerateOverview(raster._gdal_dataset.GetRasterBand(band),
                                out_ds.GetRasterBand(band), 'mode')

    # Close dataset
    out_ds = None


@_return_raster
def _rescale_raster(raster, out_file, ds_min, ds_max):

    out_ds = gdal.Translate(out_file, raster._gdal_dataset,
                            scaleParams=[[src_min, src_max, ds_min, ds_max]
                                         for src_min, src_max in zip(raster.min, raster.max)])

    # Close dataset
    out_ds = None


@_return_raster
def _set_data_type(raster, out_file, data_type):

    out_ds = gdal.Translate(out_file, raster._gdal_dataset,
                            outputType=data_type)

    # Close dataset
    out_ds = None


@_return_raster
def _set_no_data(raster, out_file, no_data):

    out_ds = gdal.Translate(out_file, raster._gdal_dataset,
                            noData=no_data)

    # Close dataset
    out_ds = None
