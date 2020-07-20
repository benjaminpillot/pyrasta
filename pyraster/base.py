# -*- coding: utf-8 -*-

""" Module summary description.

More detailed description.
"""
from functools import wraps

import gdal
import multiprocessing as mp

from pyraster import FLOAT32
from pyraster.crs import proj4_from
from pyraster.io import _copy_to_file, RasterTempFile
from pyraster.tools.conversion import _resample_raster, _padding
from pyraster.tools.exceptions import RasterBaseError
from pyraster.tools.merge import _merge
from pyraster.tools.windows import _windowing
from pyraster.utils import lazyproperty


def return_new_instance(method):
    @wraps(method)
    def _return_new_instance(self, *args, **kwargs):
        with RasterTempFile() as out_file:
            method(self, out_file.path, *args, **kwargs)
            new_self = self.__class__(out_file.path)
            new_self._temp_file = out_file

        return new_self
    return _return_new_instance


class RasterBase:

    def __init__(self, src_file):
        """ Raster class constructor

        Description
        -----------

        Parameters
        ----------
        src_file: str
            valid path to raster file
        """
        try:
            self._gdal_dataset = gdal.Open(src_file)
        except RuntimeError as e:
            raise RasterBaseError('\nGDAL returns: \"%s\"' % e)

        self._gdal_driver = self._gdal_dataset.GetDriver()
        self._file = src_file

    def __del__(self):
        self._gdal_dataset = None

    @return_new_instance
    def _pad_extent(self, out_file, pad_x, pad_y, value):
        """ Pad extent around raster
        """
        _padding(self, out_file, pad_x, pad_y, value)

    @return_new_instance
    def _resample(self, out_file, factor):
        """ Resample raster
        """
        _resample_raster(self, out_file, factor)

    # @return_new_instance
    # def _windowing(self, out_file, f_handle, band, window_size, method,
    #                data_type, no_data, chunk_size, nb_processes):
    #     """ Apply sliding window to raster
    #     """
    #     _windowing(self, out_file, f_handle, band, window_size, method,
    #                data_type, no_data, chunk_size, nb_processes)

    @classmethod
    def merge(cls, rasters, bounds=None):
        """ Merge multiple rasters

        Description
        -----------

        Parameters
        ----------
        rasters: list or tuple
            list of RasterBase instances
        bounds: tuple
            bounds of the new merged raster

        Returns
        -------
        """
        return _merge(rasters, bounds)

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
        return self._pad_extent(pad_x, pad_y, value)

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
        return self._resample(factor)

    def windowing(self, f_handle, window_size, method, band=None, data_type=FLOAT32,
                  no_data=None, chunk_size=100000, nb_processes=mp.cpu_count()):
        """ Apply function within sliding/block window

        Description
        -----------

        Parameters
        ----------
        f_handle: function
        window_size: int
            size of window
        method: str
            sliding window method ('block' or 'moving')
        band: int
            raster band
        data_type: int
            gdal data type
        no_data: list or tuple
            list of no data for each raster band
        chunk_size: int
            data chunk size for multiprocessing
        nb_processes: int
            number of processes for multiprocessing

        Return
        ------
        RasterBase:
            New instance

        """
        if band is None:
            band = 1

        if no_data is None:
            no_data = self.no_data

        # return self._windowing(f_handle, band, window_size, method,
        #                        data_type, no_data, chunk_size, nb_processes)
        return _windowing(self, f_handle, band, window_size, method,
                          data_type, no_data, chunk_size, nb_processes)

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
