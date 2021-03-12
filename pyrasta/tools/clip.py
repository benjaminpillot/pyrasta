# -*- coding: utf-8 -*-

""" Module summary description.

More detailed description.
"""
from pyrasta.io_ import ESRI_DRIVER
from pyrasta.io_.files import RasterTempFile, ShapeTempFile
from pyrasta.tools import _return_raster, _gdal_temp_dataset

import gdal


@_return_raster
def _clip_raster_by_extent(raster, out_file, bounds):

    minx = max(bounds[0], raster.bounds[0])
    miny = max(bounds[1], raster.bounds[1])
    maxx = min(bounds[2], raster.bounds[2])
    maxy = min(bounds[3], raster.bounds[2])

    if minx >= maxx or miny >= maxy:
        raise ValueError("requested extent out of raster boundaries")

    gdal.Warp(out_file,
              raster._gdal_dataset,
              outputBounds=bounds,
              srcNodata=raster.no_data,
              dstNodata=raster.no_data,
              outputType=raster.data_type)


def _clip_raster_by_feature(raster, geodataframe, id_feature, all_touched):

    feature = geodataframe.iloc[[id_feature]].to_crs(raster.crs)
    clip_raster = raster.clip(bounds=feature.bounds.iloc[id_feature].values)

    with ShapeTempFile() as out_file:

        feature.to_file(out_file.path, driver=ESRI_DRIVER)

        out_ds = _gdal_temp_dataset(clip_raster._file,
                                    clip_raster._gdal_driver,
                                    clip_raster._gdal_dataset.GetProjection(),
                                    clip_raster.x_size,
                                    clip_raster.y_size,
                                    clip_raster.nb_band,
                                    clip_raster.geo_transform,
                                    gdal.GetDataTypeByName("INT8"),
                                    no_data=-1)

        gdal.Rasterize(out_ds,
                       out_file.path,
                       burnValues=[1]*clip_raster.nb_band,
                       allTouched=all_touched)

    return clip_raster.__class__.raster_calculation([clip_raster,
                                                     clip_raster.__class__(out_file.path)],
                                                    lambda x, y: x*y)
