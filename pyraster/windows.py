# -*- coding: utf-8 -*-

""" Module summary description.

More detailed description.
"""
from numba import jit


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
