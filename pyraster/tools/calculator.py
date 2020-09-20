# -*- coding: utf-8 -*-

""" Module summary description.

More detailed description.
"""

__author__ = 'Benjamin Pillot'
__copyright__ = 'Copyright 2020, Benjamin Pillot'
__email__ = 'benjaminpillot@riseup.net'

from pyraster import FLOAT32
from pyraster.io import RasterTempFile
from pyraster.tools import _gdal_temp_dataset, _return_raster
from pyraster.tools.windows import get_block_windows
from tqdm import tqdm


@_return_raster
def _op(raster1, out_file, raster2, op_type):
    """ Basic arithmetic operations

    """
    out_ds = _gdal_temp_dataset(out_file, raster1._gdal_driver, raster1._gdal_dataset.GetProjection(), raster1.x_size,
                                raster1.y_size, raster1.nb_band, raster1.geo_transform, FLOAT32, raster1.no_data)

    for band in range(1, raster1.nb_band + 1):

        for window in get_block_windows(1000, raster1.x_size, raster1.y_size):
            array1 = raster1._gdal_dataset.GetRasterBand(band).ReadAsArray(*window).astype("float32")
            array2 = raster2._gdal_dataset.GetRasterBand(band).ReadAsArray(*window).astype("float32")

            if op_type == "add":
                result = array1 + array2
            elif op_type == "sub":
                result = array1 - array2
            elif op_type == "mul":
                result = array1 * array2
            elif op_type == "truediv":
                result = array1 / array2
            else:
                result = None

            out_ds.GetRasterBand(band).WriteArray(result, window[0], window[1])

    # Close dataset
    out_ds = None


def _raster_calculation(sources, fhandle, window_size, gdal_driver):
    """ Calculate raster expression

    """
    master_raster = sources[0]
    with RasterTempFile(gdal_driver.GetMetadata()['DMD_EXTENSION']) as out_file:

        out_ds = _gdal_temp_dataset(out_file.path, gdal_driver, master_raster._gdal_dataset.GetProjection(),
                                    master_raster.x_size, master_raster.y_size, master_raster.nb_band,
                                    master_raster.geo_transform, FLOAT32, master_raster.no_data)
        length = (master_raster.x_size//window_size + 1) * \
                 (master_raster.y_size//window_size + 1) * master_raster.nb_band

        for window in tqdm(get_block_windows(window_size, master_raster.x_size, master_raster.y_size),
                           total=length, desc="Calculate raster expression"):
            for band in range(1, master_raster.nb_band + 1):
                list_of_arrays = []
                for src in sources:
                    list_of_arrays.append(src._gdal_dataset.GetRasterBand(band).ReadAsArray(*window).astype("float32"))

                out_ds.GetRasterBand(band).WriteArray(fhandle(*list_of_arrays), window[0], window[1])

    # Close dataset
    out_ds = None

    return master_raster.__class__(out_file.path)
