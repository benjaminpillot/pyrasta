# -*- coding: utf-8 -*-

""" Module summary description.

More detailed description.
"""

import multiprocessing as mp
import numpy as np

from pyrasta.io_.files import RasterTempFile
from pyrasta.tools import _gdal_temp_dataset, _return_raster
from pyrasta.tools.windows import get_block_windows
from tqdm import tqdm

import gdal


@_return_raster
def _op(raster1, out_file, raster2, op_type):
    """ Basic arithmetic operations

    """
    out_ds = _gdal_temp_dataset(out_file, raster1._gdal_driver,
                                raster1._gdal_dataset.GetProjection(), raster1.x_size,
                                raster1.y_size, raster1.nb_band, raster1.geo_transform,
                                gdal.GetDataTypeByName('Float32'), raster1.no_data)

    for band in range(1, raster1.nb_band + 1):

        for window in get_block_windows(1000, raster1.x_size, raster1.y_size):
            array1 = raster1._gdal_dataset.GetRasterBand(
                band).ReadAsArray(*window).astype("float32")
            try:
                array2 = raster2._gdal_dataset.GetRasterBand(
                    band).ReadAsArray(*window).astype("float32")
            except AttributeError:
                array2 = raster2  # If second input is not a raster but a scalar

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


def _raster_calculation(raster_class, sources, fhandle, window_size,
                        gdal_driver, data_type, no_data, nb_processes):
    """ Calculate raster expression

    """
    master_raster = sources[0]
    with RasterTempFile(gdal_driver.GetMetadata()['DMD_EXTENSION']) as out_file:

        is_first_run = True
        y = 0
        pgbar = tqdm(total=master_raster.y_size // window_size + int(master_raster.y_size %
                                                                     window_size != 0),
                     desc="Calculate raster expression")

        while y < master_raster.y_size:

            y_size = min(window_size, master_raster.y_size - y)

            arrays = []
            for src in sources:
                array = src._gdal_dataset.ReadAsArray(0, y, None, y_size).astype("float32")
                array[array == src.no_data] = np.nan
                arrays.append(array)

            window_gen = ([array[w[1]:w[1] + w[3], w[0]:w[0] + w[2]] for array in arrays] for w
                          in get_block_windows(window_size, master_raster.x_size, y_size))

            with mp.Pool(processes=nb_processes) as pool:
                result = np.concatenate(list(pool.imap(fhandle, window_gen)), axis=1)

            result[np.isnan(result)] = no_data

            pgbar.update(1)

            if is_first_run:
                if result.ndim == 2:
                    nb_band = 1
                else:
                    nb_band = result.shape[0]

                out_ds = _gdal_temp_dataset(out_file.path,
                                            gdal_driver,
                                            master_raster._gdal_dataset.GetProjection(),
                                            master_raster.x_size,
                                            master_raster.y_size, nb_band,
                                            master_raster.geo_transform,
                                            data_type,
                                            no_data)

                is_first_run = False

            if nb_band == 1:
                out_ds.GetRasterBand(1).WriteArray(result, 0, y)
            else:
                for band in range(nb_band):
                    out_ds.GetRasterBand(band + 1).WriteArray(result[band, :, :],
                                                              0, y)

            y += window_size

    # Close dataset
    out_ds = None

    return raster_class(out_file.path)
