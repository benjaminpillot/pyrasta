# -*- coding: utf-8 -*-

""" Module summary description.

More detailed description.
"""
from functools import wraps, partial

from numba import jit
from tqdm import tqdm

import multiprocessing as mp
import numpy as np

from pyrasta.tools import _gdal_temp_dataset, _return_raster
from pyrasta.exceptions import WindowGeneratorError
from pyrasta.utils import split_into_chunks, check_string, check_type, MP_CHUNK_SIZE


def _set_nan(array, function, no_data):
    """ Replace no data values by NaNs

    """
    array[array == no_data] = np.nan
    return function(array)


@_return_raster
def _windowing(raster, out_file, function, band, window_size,
               method, data_type, no_data, chunk_size, nb_processes):
    """ Apply function in each moving or block window in raster

    Description
    -----------

    Parameters
    ----------

    """
    window_generator = WindowGenerator(raster, band, window_size, method)
    out_ds = _gdal_temp_dataset(out_file, raster._gdal_driver, raster._gdal_dataset.GetProjection(),
                                window_generator.x_size, window_generator.y_size, raster.nb_band,
                                window_generator.geo_transform, data_type, no_data)

    y = 0
    # chunk size cannot be 0 and cannot
    # be higher than height of window
    # generator (y_size). And it must be
    # a multiple of window generator width
    # (x_size)
    chunk_size = max(min(chunk_size // window_generator.x_size, window_generator.y_size)
                     * window_generator.x_size, window_generator.x_size)
    for win_gen in tqdm(split_into_chunks(window_generator, chunk_size),
                        total=len(window_generator)//chunk_size +
                        int(len(window_generator) % chunk_size != 0),
                        desc="Sliding window computation"):
        with mp.Pool(processes=nb_processes) as pool:
            output = np.asarray(list(pool.imap(partial(_set_nan,
                                                       function=function,
                                                       no_data=raster.no_data),
                                               win_gen,
                                               chunksize=MP_CHUNK_SIZE)))

        output[np.isnan(output)] = no_data

        # Set number of rows to write to file
        n_rows = len(output) // window_generator.x_size

        # Write row to raster
        out_ds.GetRasterBand(band).WriteArray(np.reshape(output, (n_rows,
                                                                  window_generator.x_size)), 0, y)

        # Update row index
        y += n_rows

    # Close dataset
    out_ds = None


def integer(setter):

    @wraps(setter)
    def _integer(self, value):
        try:
            check_type(value, int)
        except TypeError:
            raise WindowGeneratorError("'%s' must be an integer value but is: '%s'" %
                                       (setter.__name__, type(value).__name__))
        output = setter(self, value)

    return _integer


def odd(setter):

    @wraps(setter)
    def _odd(self, value):
        if value % 2 == 0:
            raise WindowGeneratorError("'%s' must be an odd value (=%d)" % (setter.__name__, value))
        output = setter(self, value)

    return _odd


def positive(setter):

    @wraps(setter)
    def _positive(self, value):
        if value <= 0:
            raise WindowGeneratorError("'%s' must be positive (=%d)" % (setter.__name__, value))
        output = setter(self, value)

    return _positive


class WindowGenerator:
    """ Generator of windows over raster

    """

    def __init__(self, raster, band, window_size, method):
        """ WindowGenerator constructor

        Description
        -----------

        Parameters
        ----------
        raster: RasterBase
            raster for which we must compute windows
        band: int
            raster band number
        window_size: int
            size of window in pixels
        method: str
            sliding window method ("block" or "moving")

        Return
        ------

        """
        self.band = band
        self.raster = raster
        self.window_size = window_size
        self.method = method

        # self.image = self.raster._gdal_dataset.GetRasterBand(self.band).ReadAsArray()

    @property
    def geo_transform(self):
        if self.method == "block":
            topleftx, pxsizex, rotx, toplefty, roty, pxsizey = \
                self.raster._gdal_dataset.GetGeoTransform()
            return topleftx, pxsizex * self.window_size, rotx, \
                toplefty, roty, pxsizey * self.window_size
        else:
            return self.raster._gdal_dataset.GetGeoTransform()

    @property
    def method(self):
        return self._method

    @method.setter
    def method(self, value):
        try:
            self._method = check_string(value, {'block', 'moving'})
        except (TypeError, ValueError) as e:
            raise WindowGeneratorError("Invalid sliding window method: '%s'" % value)

    @property
    def band(self):
        return self._band

    @band.setter
    @integer
    @positive
    def band(self, value):
        self._band = value

    @property
    def window_size(self):
        return self._window_size

    @window_size.setter
    @integer
    @positive
    def window_size(self, value):
        self._window_size = value

    @property
    def x_size(self):
        if self.method == "block":
            return int(self.raster.x_size / self.window_size) + \
                   min(1, self.raster.x_size % self.window_size)
        else:
            return self.raster.x_size

    @property
    def y_size(self):
        if self.method == "block":
            return int(self.raster.y_size / self.window_size) + \
                   min(1, self.raster.y_size % self.window_size)
        else:
            return self.raster.y_size

    def __len__(self):
        return self.y_size * self.x_size

    def __iter__(self):
        def windows():
            if self.method == "block":
                return get_block_windows(self.window_size, self.raster.x_size, self.raster.y_size)
            elif self.method == "moving":
                return get_moving_windows(self.window_size, self.raster.x_size, self.raster.y_size)

        return (self.raster._gdal_dataset.GetRasterBand(self.band).ReadAsArray(*window).astype(
            "float32") for window in windows())
        # return (self.image[w[1]:w[1] + w[3], w[0]:w[0] + w[2]] for w in windows())


@jit(nopython=True, nogil=True)
def get_xy_block_windows(window_size, raster_x_size, raster_y_size):
    """ Get xy block window coordinates

    Description
    -----------
    Get xy block window coordinates depending
    on raster size and window size

    Parameters
    ----------
    window_size: (int, int)
        size of window to read within raster as (width, height)
    raster_x_size: int
        raster's width
    raster_y_size: int
        raster's height

    Yields
    -------
    Window coordinates: tuple
        4-element tuple returning the coordinates of the window within the raster
    """
    for y in range(0, raster_y_size, window_size[1]):
        ysize = min(window_size[1], raster_y_size - y)
        for x in range(0, raster_x_size, window_size[0]):
            xsize = min(window_size[0], raster_x_size - x)

            yield x, y, xsize, ysize


@jit(nopython=True, nogil=True)
def get_block_windows(window_size, raster_x_size, raster_y_size):
    """ Get block window coordinates

    Description
    -----------
    Get block window coordinates depending
    on raster size and window size

    Parameters
    ----------
    window_size: int
        size of window to read within raster
    raster_x_size: int
        raster's width
    raster_y_size: int
        raster's height

    Yields
    -------
    Window coordinates: tuple
        4-element tuple returning the coordinates of the window within the raster
    """
    for y in range(0, raster_y_size, window_size):
        ysize = min(window_size, raster_y_size - y)
        for x in range(0, raster_x_size, window_size):
            xsize = min(window_size, raster_x_size - x)

            yield x, y, xsize, ysize


@jit(nopython=True, nogil=True)
def get_moving_windows(window_size, raster_x_size, raster_y_size, step=1):
    """ Get moving window coordinates

    Description
    -----------
    Get moving window coordinates depending
    on raster size, window size and step

    Parameters
    ----------
    window_size: int
        size of window (square)
    raster_x_size: int
        raster's width
    raster_y_size: int
        raster's height
    step: int
        gap between the window's centers when moving the window over the raster

    Yields
    -------
    Window coordinates: tuple
        tuple of coordinates
    """
    offset = int((window_size - 1) / 2)  # window_size must be an odd number
    # for each pixel, compute indices of the window (all included)
    for y in range(0, raster_y_size, step):
        y1 = max(0, y - offset)
        y2 = min(raster_y_size - 1, y + offset)
        ysize = (y2 - y1) + 1
        for x in range(0, raster_x_size, step):
            x1 = max(0, x - offset)
            x2 = min(raster_x_size - 1, x + offset)
            xsize = (x2 - x1) + 1

            yield x1, y1, xsize, ysize
