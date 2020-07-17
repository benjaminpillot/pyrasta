# -*- coding: utf-8 -*-

""" Module summary description.

More detailed description.
"""
import os
from functools import wraps, partial

import gdal
import multiprocessing as mp

from pyraster import FLOAT32
from pyraster.crs import proj4_from
from pyraster.io import _copy_to_file
from pyraster.tools.conversion import _resample_raster, _padding
from pyraster.tools.merge import _merge
from pyraster.tools.windows import _windowing
from pyraster.utils import lazyproperty


def return_new_instance(method):
    @wraps(method)
    def _return_new_instance(self, *args, **kwargs):
        output = method(self, *args, **kwargs)
        new_self = self.__class__(output)
        new_self._temporary_files.append(output)

        return new_self
        # try:
        # except RuntimeError:
        #     return output
    return _return_new_instance


class RasterBase:

    # Class attribute that is mutable
    # This is on purpose so that we keep track
    # of all instances based on temp files
    _temporary_files = []

    def __init__(self, src_file):
        """ Raster class constructor

        """
        self._file = src_file
        self._gdal_dataset = gdal.Open(src_file)
        self._gdal_driver = self._gdal_dataset.GetDriver()

    def __del__(self):
        self._gdal_dataset = None
        if self._file in self._temporary_files:
            self._temporary_files.remove(self._file)
            os.remove(self._file)

    @classmethod
    def merge(cls, rasters, bounds=None):

        return _merge(rasters, bounds)

    @return_new_instance
    def pad_extent(self, pad_x, pad_y, value):
        """ Pad raster extent with given values

        Description
        -----------
        Pad raster extent, i.e. add pad value around raster bounds

        Parameters
        ----------
        pad_x: int
            x padding size (new width will therefore be RasterXSize + 2 * pad_x)
        pad_y: int
            y padding size (new height will therefore be RasterYSize + 2 * pad_y)
        value: int or float
            value to set to pad area around raster

        Returns
        -------
        RasterBase:
            New instance
        """
        return _padding(self, pad_x, pad_y, value)

    @return_new_instance
    def resample(self, factor):
        """ Resample raster

        Description
        -----------
        Resample raster with respect to resampling factor.
        The higher the factor, the higher the resampling.

        Parameters
        ----------
        factor: int or float
            Resampling factor

        Returns
        -------
        RasterBase:
            New temporary resampled instance
        """
        return _resample_raster(self, factor)

    def to_file(self, filename):
        """ Write raster copy to file

        Description
        -----------
        Write raster to given file

        Parameters
        ----------
        filename: str
            File path to write to

        Return
        ------
        """
        return _copy_to_file(self, filename)

    @return_new_instance
    def windowing(self, window_size, method, f_handle, f_kwargs=None, data_type=FLOAT32, no_data=None,
                  nb_processes=mp.cpu_count()):
        """ Apply function within sliding/block window

        Description
        -----------

        Parameters
        ----------

        Return
        ------
        RasterBase:
            New instance

        """
        if f_kwargs is None:
            return _windowing(self, f_handle, window_size, method, data_type, no_data, nb_processes)
        else:
            return _windowing(self, partial(f_handle, **f_kwargs), window_size,
                              method, data_type, no_data, nb_processes)

    @property
    def crs(self):
        return proj4_from(self._gdal_dataset.GetProjection())

    @lazyproperty
    def bounds(self):
        return self.x_origin, self.y_origin - self.resolution[1] * self.y_size, \
               self.x_origin + self.resolution[0] * self.x_size, self.y_origin

    @lazyproperty
    def geo_transform(self):
        return self._gdal_dataset.GetGeoTransform()

    @lazyproperty
    def nb_band(self):
        return self._gdal_dataset.RasterCount

    @lazyproperty
    def no_data(self):
        return [self._gdal_dataset.GetRasterBand(band + 1).GetNoDataValue() for band in range(self.nb_band)]

    @lazyproperty
    def resolution(self):
        return self.geo_transform[1], abs(self.geo_transform[5])

    @lazyproperty
    def x_origin(self):
        return self.geo_transform[0]

    @lazyproperty
    def x_size(self):
        return self._gdal_dataset.RasterXSize

    @lazyproperty
    def y_origin(self):
        return self.geo_transform[3]

    @lazyproperty
    def y_size(self):
        return self._gdal_dataset.RasterYSize
