# -*- coding: utf-8 -*-

""" Module summary description.

More detailed description.
"""
from pyrasta.io_.files import RasterTempFile

import gdal
from pyrasta.tools import _return_raster


@_return_raster
def _merge(raster_class, out_file, gdal_driver,
           sources, bounds, data_type, no_data):
    """ Merge multiple raster sources

    """

    # Extent of all inputs
    if bounds is not None:
        dst_w, dst_s, dst_e, dst_n = bounds
    else:
        # scan input files
        xs = [item for src in sources for item in src.bounds[0:2]]
        ys = [item for src in sources for item in src.bounds[2::]]
        dst_w, dst_s, dst_e, dst_n = min(xs), min(ys), max(xs), max(ys)

    gdal.Warp(out_file, [src._gdal_dataset for src in sources],
              outputBounds=(dst_w, dst_s, dst_e, dst_n),
              format=gdal_driver.GetDescription(),
              srcNodata=[src.no_data for src in sources],
              dstNodata=no_data, outputType=data_type)

    # Be careful with the temp file, make a pointer to be sure
    # the Python garbage collector does not destroy it !
    # raster = raster_class(out_file.path)
    # raster._temp_file = out_file
    #
    # return raster


# def _rasterio_merge_modified(sources, out_file, bounds=None, driver="GTiff", precision=7):
#     """ Modified rasterio merge
#
#     Description
#     -----------
#     Merge set of rasters using modified
#     rasterio merging tool. Only import as
#     numpy arrays the source datasets, and
#     write each source to destination raster.
#
#     Parameters
#     ----------
#     sources: list
#         list of rasterio datasets
#     out_file: str
#         valid path to the raster file to be written
#     bounds: tuple
#         valid boundary tuple (optional)
#     driver: str
#         valid gdal driver (optional)
#     precision: int
#         float precision (optional)
#
#     Note
#     ----
#     Adapted from
#     https://gis.stackexchange.com/questions/348925/merging-rasters-with-rasterio-in-blocks-to-avoid-memoryerror
#     """
#
    # adapted from https://github.com/mapbox/rasterio/blob/master/rasterio/merge.py
    # first = sources[0]
    # first_res = first.res
    # dtype = first.dtypes[0]
    # Determine output band count
    # output_count = first.count

    # Extent of all inputs
    # if bounds:
    #     dst_w, dst_s, dst_e, dst_n = bounds
    # else:
        # scan input files
        # xs = []
        # ys = []
        # for src in sources:
        #     left, bottom, right, top = src.bounds
        #     xs.extend([left, right])
        #     ys.extend([bottom, top])
        # dst_w, dst_s, dst_e, dst_n = min(xs), min(ys), max(xs), max(ys)
    #
    # out_transform = Affine.translation(dst_w, dst_n)
    #
    # Resolution/pixel size
    # res = first_res
    # out_transform *= Affine.scale(res[0], -res[1])
    #
    # Compute output array shape. We guarantee it will cover the output
    # bounds completely
    # output_width = int(np.ceil((dst_e - dst_w) / res[0]))
    # output_height = int(np.ceil((dst_n - dst_s) / res[1]))

    # Adjust bounds to fit
    # dst_e, dst_s = out_transform * (output_width, output_height)

    # create destination array
    # destination array shape
    # shape = (output_height, output_width)
    #
    # dest_profile = {
    #     "driver": driver,
    #     "height": shape[0],
    #     "width": shape[1],
    #     "count": output_count,
    #     "dtype": dtype,
    #     "crs": sources[0].crs.to_proj4(),
    #     "nodata": sources[0].nodata,
    #     "transform": out_transform
    # }

    # open output file in write/read mode and fill with destination mosaick array
    # with rasterio.open(out_file, 'w+', **dest_profile) as mosaic_raster:
    #     for src in sources:

            # 1. Compute spatial intersection of destination and source
            # src_w, src_s, src_e, src_n = src.bounds
            # int_w = src_w if src_w > dst_w else dst_w
            # int_s = src_s if src_s > dst_s else dst_s
            # int_e = src_e if src_e < dst_e else dst_e
            # int_n = src_n if src_n < dst_n else dst_n

            # 2. Compute the source window
            # src_window = windows.from_bounds(
            #     int_w, int_s, int_e, int_n, src.transform, precision=precision)
            #
            # src_window = src_window.round_shape()

            # 3. Compute the destination window
            # dst_window = windows.from_bounds(
            #     int_w, int_s, int_e, int_n, out_transform, precision=precision)
            # dst_window = windows.Window(int(round(dst_window.col_off)),
            #                             int(round(dst_window.row_off)),
            #                             int(round(dst_window.width)),
            #                             int(round(dst_window.height)))
            #
            # out_shape = (dst_window.height, dst_window.width)

            # for band in range(1, output_count+1):
            #     src_array = src.read(band, out_shape=out_shape, window=src_window)
                # before writing the window, replace source nodata with dest nodata as it can
                # already have been written (e.g. another adjacent country)
                # dst_array = mosaic_raster.read(band, out_shape=out_shape, window=dst_window)
                # mask = src_array == src.nodata
                # src_array[mask] = dst_array[mask]
                # mosaic_raster.write(src_array, band, window=dst_window)
