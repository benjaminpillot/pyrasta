# -*- coding: utf-8 -*-

""" Module summary description.

More detailed description.
"""
import numpy as np
from collections import Collection
from itertools import chain, islice

from numba import njit
from tqdm import tqdm


MP_CHUNK_SIZE = 1000


class TqdmUpTo(tqdm):
    """ Progress bar for url retrieving

    Description
    -----------
    Thanks to https://github.com/tqdm/tqdm/blob/master/examples/tqdm_wget.py

    Provides `update_to(n)` which uses `tqdm.update(delta_n)`.
    Inspired by [twine#242](https://github.com/pypa/twine/pull/242),
    [here](https://github.com/pypa/twine/commit/42e55e06).
    """

    def update_to(self, b=1, bsize=1, tsize=None):
        """
        b  : int, optional
            Number of blocks transferred so far [default: 1].
        bsize  : int, optional
            Size of each block (in tqdm units) [default: 1].
        tsize  : int, optional
            Total size (in tqdm units). If [default: None] remains unchanged.
        """
        if tsize is not None:
            self.total = tsize
        return self.update(b * bsize - self.n)  # also sets self.n = b * bsize


def check_string(string, list_of_strings):
    """ Check validity of and return string against list of valid strings

    :param string: searched string
    :param list_of_strings: list/tuple/set of valid strings string is to be checked against
    :return: validate string from list of strings if match
    """
    check_type(string, str, list_of_strings, Collection)
    [check_type(x, str) for x in list_of_strings]

    output_string = []

    for item in list_of_strings:
        if item.lower().startswith(string.lower()):
            output_string.append(item)

    if len(output_string) == 1:
        return output_string[0]
    elif len(output_string) == 0:
        raise ValueError("input must match one of those: {}".format(list_of_strings))
    elif len(output_string) > 1:
        raise ValueError("input match more than one valid value among {}".format(list_of_strings))


def check_type(*args):
    """Check type of arguments

    :param args: tuple list of argument/type
    :return:
    """
    if len(args) % 2 == 0:
        for item in range(0, len(args), 2):
            if not isinstance(args[item], args[item + 1]):
                raise TypeError("Type of argument {} is '{}' but must be '{}'".format(
                    item//2 + 1, type(args[item]).__name__, args[item + 1].__name__))


def digitize(value, list_of_values, ascend=True, right=False):
    """

    Description
    -----------

    Parameters
    ----------

    """
    if ascend:
        loc = [value > v if right else value >= v for v in list_of_values]
    else:
        loc = [value <= v if right else value < v for v in list_of_values]

    return loc.index(False) if False in loc else len(list_of_values)


def gdal_progress_bar(display, description):

    if display:
        callback = gdal_progress_callback
        callback_data = tqdm(desc=description, total=100)
    else:
        callback = None
        callback_data = None

    return callback, callback_data


def gdal_progress_callback(complete, message, tqdm_pg):
    if complete >= 1:
        tqdm_pg.close()
    else:
        tqdm_pg.update(1)


@njit()
def grid(origin, resolution, size):
    """ Return regular grid vector

    Parameters
    ----------
    origin
    resolution
    size

    Returns
    -------

    """
    origin -= resolution

    for _ in range(size):
        origin += resolution

        yield origin


def isnan(value):
    try:
        return np.isnan(value)
    except TypeError:
        return False


def lazyproperty(func):
    name = '_lazy_' + func.__name__

    @property
    def lazy(self):
        if hasattr(self, name):
            return getattr(self, name)
        else:
            value = func(self)
            setattr(self, name, value)
            return value
    return lazy


def split_into_chunks(iterable, size):
    """ Split iterable into chunks of iterables

    """
    iterator = iter(iterable)
    for first in iterator:
        yield chain([first], islice(iterator, size - 1))
