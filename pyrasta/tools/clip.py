# -*- coding: utf-8 -*-

""" Module summary description.

More detailed description.
"""
from functools import partial

from pyrasta.io_ import ESRI_DRIVER
from pyrasta.io_.files import RasterTempFile, ShapeTempFile, GeojsonTempFile
from pyrasta.tools import _return_raster, _gdal_temp_dataset

try:
    from osgeo import gdal
except ImportError:
    import gdal


@_return_raster
def _clip_raster_by_extent(raster, out_file, bounds, no_data):
    """ Clip raster by extent

    Parameters
    ----------
    raster: pyrasta.raster.RasterBase
    out_file: pyrasta.io_.files.RasterTempFile
    bounds: tuple
        boundaries as (minx, miny, maxx, maxy)
    no_data: int or float
        No data value

    Returns
    -------
    RasterBase

    """

    minx = max(bounds[0], raster.bounds[0])
    miny = max(bounds[1], raster.bounds[1])
    maxx = min(bounds[2], raster.bounds[2])
    maxy = min(bounds[3], raster.bounds[3])

    if minx >= maxx or miny >= maxy:
        raise ValueError("requested extent out of raster boundaries")

    # gdal.Translate projWin as [upper left x, upper left y, lower right x, lower right y]
    gdal.Translate(out_file,
                   raster._gdal_dataset,
                   projWin=[minx, maxy, maxx, miny])

    # gdal.Warp(out_file,
    #           raster._gdal_dataset,
    #           outputBounds=bounds,
    #           srcNodata=raster.no_data,
    #           dstNodata=no_data,
    #           outputType=raster.data_type)


def _clip_raster_by_mask(raster, geodataframe, no_data, all_touched, driver):
    """ Clip raster by mask from geographic layer

    Parameters
    ----------
    raster: pyrasta.raster.RasterBase
        raster to clip
    geodataframe: geopandas.GeoDataFrame or gistools.layer.GeoLayer
    no_data: float or int
        No data value in output raster
    all_touched: bool
        if True, clip all pixels that are touched, otherwise clip
        if pixel's centroids are within boundaries

    Returns
    -------
    RasterBase

    """
    clip_raster = raster.clip(bounds=geodataframe.total_bounds, no_data=no_data)

    if driver == "ESRI Shapefile":
        temp_file = ShapeTempFile
    else:
        temp_file = GeojsonTempFile

    with temp_file() as tempfile, \
            RasterTempFile(clip_raster._gdal_driver.GetMetadata()['DMD_EXTENSION']) as r_file:

        geodataframe.to_file(tempfile.path, driver=driver)

        out_ds = _gdal_temp_dataset(r_file.path,
                                    clip_raster._gdal_driver,
                                    clip_raster._gdal_dataset.GetProjection(),
                                    clip_raster.x_size,
                                    clip_raster.y_size,
                                    clip_raster.nb_band,
                                    clip_raster.geo_transform,
                                    clip_raster.data_type,
                                    clip_raster.no_data)

        gdal.Rasterize(out_ds,
                       tempfile.path,
                       bands=list(range(1, clip_raster.nb_band + 1)),
                       burnValues=[1] * clip_raster.nb_band,
                       allTouched=all_touched)

    out_ds = None

    return clip_raster.__class__.raster_calculation([clip_raster,
                                                     clip_raster.__class__(r_file.path)],
                                                    partial(mask_clip, no_data=no_data),
                                                    no_data=no_data,
                                                    description=None)


def mask_clip(arrays, no_data):

    result = arrays[0] * arrays[1]
    result[arrays[1] != 1] = no_data

    return result
