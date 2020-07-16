# -*- coding: utf-8 -*-

""" Module summary description.

More detailed description.
"""
from numba import jit
from tqdm import tqdm

import multiprocessing as mp
import numpy as np

from pyraster.io import RasterTempFile
from pyraster.utils import split_into_chunks, check_string


def _windowing(raster, function, window_size, method, nb_processes=mp.cpu_count()):
    """ Apply function in each moving or block window in raster

    Description
    -----------

    Parameters
    ----------

    """
    check_string(method, ('block', 'moving'))

    window_generator = WindowGenerator(raster, window_size, method)

    with RasterTempFile() as out_file:
        out_ds = raster._gdal_driver.Create(out_file, window_generator.x_size, window_generator.y_size, raster.nb_band,
                                            raster._gdal_dataset.GetRasterBand(1).DataType)
    out_ds.SetGeoTransform(window_generator.geo_transform)
    out_ds.SetProjection(raster._gdal_dataset.GetProjection())

    band = 1
    y = 0
    for win_gen in tqdm(split_into_chunks(window_generator, window_generator.x_size),
                        total=len(window_generator)//window_generator.x_size + 1, desc="Sliding window"):
        with mp.Pool(processes=nb_processes) as pool:
            output = np.expand_dims(list(pool.map(function, win_gen,
                                                  chunksize=window_generator.x_size//nb_processes)), axis=0)

        # Write row to raster
        out_ds.GetRasterBand(band).WriteArray(output, 0, y)

        # Update row index + band number if necessary
        y += 1
        if y == raster.y_size:
            y = 0
            band += 1

    # Close dataset
    out_ds = None

    return out_file


class WindowGenerator:
    """ Generator of windows over raster

    """

    def __init__(self, raster, window_size, method):
        """ WindowGenerator constructor

        Description
        -----------

        Parameters
        ----------
        raster: RasterBase
            raster for which we must compute windows
        window_size: int
            size of window in pixels
        method: str
            sliding window method ("block" or "moving")

        Return
        ------

        """
        self.raster = raster
        self.window_size = window_size
        self.method = method

    @property
    def geo_transform(self):
        if self.method == "block":
            topleftx, pxsizex, rotx, toplefty, roty, pxsizey = self.raster._gdal_dataset.GetGeoTransform()
            return topleftx, pxsizex * self.window_size, rotx, toplefty, roty, pxsizey * self.window_size
        else:
            return self.raster._gdal_dataset.GetGeoTransform()

    @property
    def x_size(self):
        if self.method == "block":
            return int(self.raster.x_size / self.window_size) + min(1, self.raster.x_size % self.window_size)
        else:
            return self.raster.x_size

    @property
    def y_size(self):
        if self.method == "block":
            return int(self.raster.y_size / self.window_size) + min(1, self.raster.y_size % self.window_size)
        else:
            return self.raster.y_size

    def __len__(self):
        return self.y_size * self.x_size * self.raster.nb_band

    def __iter__(self):
        def windows():
            if self.method == "block":
                return get_block_windows(self.window_size, self.raster.x_size, self.raster.y_size)
            elif self.method == "moving":
                return get_moving_windows(self.window_size, self.raster.x_size, self.raster.y_size)

        return (self.raster._gdal_dataset.GetRasterBand(band + 1).ReadAsArray(*window)
                for band in range(self.raster.nb_band) for window in windows())


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
