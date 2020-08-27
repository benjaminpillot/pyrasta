# -*- coding: utf-8 -*-

""" Module summary description.

More detailed description.
"""

import gdal
import multiprocessing as mp

from pyraster import FLOAT32
from pyraster.crs import proj4_from
from pyraster.io import _copy_to_file
from pyraster.tools.conversion import _resample_raster, _padding, _rescale_raster
from pyraster.tools.exceptions import RasterBaseError
from pyraster.tools.merge import _merge
from pyraster.tools.stats import _histogram
from pyraster.tools.windows import _windowing
from pyraster.utils import lazyproperty


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

    def histogram(self, nb_bins=10, normalized=True):
        """ Compute raster histogram

        Description
        -----------

        Parameters
        ----------
        nb_bins: int
            number of bins for histogram
        normalized: bool
            if True, normalize histogram frequency values

        Returns
        -------

        """
        return _histogram(self, nb_bins, normalized)

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
        return _padding(self, pad_x, pad_y, value)

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

    def rescale(self, r_min, r_max):
        """ Rescale values from raster

        Description
        -----------

        Parameters
        ----------
        r_min: int or float
            minimum value of new range
        r_max: int or float
            maximum value of new range

        Return
        ------
        """
        return _rescale_raster(self, r_min, r_max)

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
    def max(self):
        return [self._gdal_dataset.GetRasterBand(band + 1).ComputeRasterMinMax()[1] for band in range(self.nb_band)]

    @lazyproperty
    def min(self):
        return [self._gdal_dataset.GetRasterBand(band + 1).ComputeRasterMinMax()[0] for band in range(self.nb_band)]

    @lazyproperty
    def nb_band(self):
        return self._gdal_dataset.RasterCount

    @lazyproperty
    def no_data(self):
        return [self._gdal_dataset.GetRasterBand(band + 1).GetNoDataValue() for band in range(self.nb_band)]

    @lazyproperty
    def data_type(self):
        return self._gdal_dataset.GetRasterBand(1).DataType

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
