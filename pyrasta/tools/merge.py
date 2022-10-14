# -*- coding: utf-8 -*-

""" Module summary description.

More detailed description.
"""
from pyrasta.tools import _return_raster

try:
    from osgeo import gdal
except ImportError:
    import gdal


@_return_raster
def _merge(raster_class, out_file, gdal_driver,
           sources, bounds, data_type, input_no_data,
           output_no_data, resampling_mode):
    """ Merge multiple raster sources

    """

    # Extent of all inputs
    if bounds is not None:
        dst_w, dst_s, dst_e, dst_n = bounds
    else:
        # scan input files
        xs = [item for src in sources for item in src.bounds[0::2]]
        ys = [item for src in sources for item in src.bounds[1::2]]
        dst_w, dst_s, dst_e, dst_n = min(xs), min(ys), max(xs), max(ys)

    gdal.Warp(out_file, [src._gdal_dataset for src in sources],
              outputBounds=(dst_w, dst_s, dst_e, dst_n),
              format=gdal_driver.GetDescription(),
              srcNodata=input_no_data,
              dstNodata=output_no_data,
              outputType=data_type,
              resampleAlg=resampling_mode)
