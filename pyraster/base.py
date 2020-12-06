# -*- coding: utf-8 -*-

""" Module summary description.

More detailed description.
"""

import gdal
import multiprocessing as mp

from pyraster import FLOAT32
from pyraster.crs import proj4_from
from pyraster._io import _copy_to_file
from pyraster.tools.calculator import _op, _raster_calculation
from pyraster.tools.conversion import _resample_raster, _padding, _rescale_raster, _align_raster, _extract_bands, \
    _merge_bands
from pyraster.tools.exceptions import RasterBaseError
from pyraster.tools.merge import _merge
from pyraster.tools.stats import _histogram
from pyraster.tools.windows import _windowing
from pyraster.utils import lazyproperty


class RasterBase:

    def __init__(self, src_file, no_data=None):
        """ Raster class constructor

        Description
        -----------

        Parameters
        ----------
        src_file: str
            valid path to raster file
        no_data: int or float
            Set no data value only if it is not already defined in raster file
        """
        try:
            self._gdal_dataset = gdal.Open(src_file)
        except RuntimeError as e:
            raise RasterBaseError('\nGDAL returns: \"%s\"' % e)

        # If NoData not defined, define here
        for band in range(self.nb_band):
            if self._gdal_dataset.GetRasterBand(band + 1).GetNoDataValue() is None:
                self._gdal_dataset.GetRasterBand(band + 1).SetNoDataValue(no_data)

        self._gdal_driver = self._gdal_dataset.GetDriver()
        self._file = src_file

    def __add__(self, other):
        """ Add two raster

        """
        return _op(self, other, "add")

    def __sub__(self, other):
        """ Subtract two raster

        """
        return _op(self, other, "sub")

    def __mul__(self, other):
        """ Multiply two raster

        """
        return _op(self, other, "mul")

    def __truediv__(self, other):
        """ Divide two raster

        """
        return _op(self, other, "truediv")

    def __del__(self):
        self._gdal_dataset = None

    def align_raster(self, other):
        """ Align raster on other

        Description
        -----------

        Parameters
        ----------
        other: RasterBase
            other RasterBase instance

        """

        return _align_raster(self, other)

    def extract_bands(self, bands):
        """ Extract bands as multiple rasters

        Description
        -----------

        Parameters
        ----------
        bands: list
            list of band numbers
        """
        return _extract_bands(self, bands)

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
    def merge(cls, rasters, bounds=None, output_format="Gtiff", data_type=FLOAT32, no_data=-999):
        """ Merge multiple rasters

        Description
        -----------

        Parameters
        ----------
        rasters: Collection
            Collection of RasterBase instances
        bounds: tuple
            bounds of the new merged raster
        output_format:str
            raster file output format (Gtiff, etc.)
        data_type: int
            GDAL data type
        no_data: int or float
            output no data value in merged raster

        Returns
        -------

        """
        return _merge(rasters, bounds, output_format, data_type, no_data)

    @classmethod
    def merge_bands(cls, rasters, resolution="highest", gdal_driver=gdal.GetDriverByName("Gtiff"), no_data=-999):
        """ Create one single raster from multiple bands

        Description
        -----------
        Create one raster from multiple bands using gdal

        Parameters
        ----------
        rasters: Collection
            Collection of RasterBase instances
        resolution: str
            GDAL resolution option ("highest", "lowest", "average")
        gdal_driver: osgeo.gdal.Driver
        no_data: int or float
            no data value in output raster
        """
        return _merge_bands(cls, rasters, resolution, gdal_driver, no_data)

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
        RasterBase
            A padded RasterBase
        """
        return _padding(self, pad_x, pad_y, value)

    @classmethod
    def raster_calculation(cls, rasters, fhandle, window_size=1000, gdal_driver=gdal.GetDriverByName("Gtiff"),
                           data_type=FLOAT32, no_data=-999, **kwargs):
        """ Raster expression calculation

        Description
        -----------
        Calculate raster expression stated in "fhandle"
        such as: fhandle(raster1, raster2, etc.)
        Calculation is made for each band.

        Parameters
        ----------
        rasters: list or tuple
            collection of RasterBase instances
        fhandle: function
            expression to calculate
        window_size: int
            size of window/chunk to set in memory during calculation
        gdal_driver: osgeo.gdal.Driver
            GDAL driver (output format)
        data_type: int
            GDAL data type for output raster
        no_data: int or float
            no data value in resulting raster
        kwargs:
            fhandle keyword arguments (if any)

        Returns
        -------
        RasterBase:
            New temporary instance
        """
        return _raster_calculation(cls, rasters, fhandle, window_size, gdal_driver, data_type, no_data, **kwargs)

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
            raster no data
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

        return _windowing(self, f_handle, band, window_size, method,
                          data_type, no_data, chunk_size, nb_processes)

    @property
    def crs(self):
        """ Return Coordinate Reference System

        """
        return proj4_from(self._gdal_dataset.GetProjection())

    @lazyproperty
    def bounds(self):
        """ Return raster bounds

        """
        return self.x_origin, self.y_origin - self.resolution[1] * self.y_size, \
            self.x_origin + self.resolution[0] * self.x_size, self.y_origin

    @lazyproperty
    def geo_transform(self):
        return self._gdal_dataset.GetGeoTransform()

    @lazyproperty
    def max(self):
        """ Return raster maximum value for each band

        """
        return [self._gdal_dataset.GetRasterBand(band + 1).ComputeRasterMinMax()[1]
                for band in range(self.nb_band)]

    @lazyproperty
    def mean(self):
        """ Compute raster mean for each band

        """
        return [self._gdal_dataset.GetRasterBand(band + 1).ComputeStatistics(False)[2]
                for band in range(self.nb_band)]

    @lazyproperty
    def min(self):
        """ Return raster minimum value for each band

        """
        return [self._gdal_dataset.GetRasterBand(band + 1).ComputeRasterMinMax()[0]
                for band in range(self.nb_band)]

    @lazyproperty
    def nb_band(self):
        """ Return raster number of bands

        """
        return self._gdal_dataset.RasterCount

    @lazyproperty
    def no_data(self):
        # return [self._gdal_dataset.GetRasterBand(band + 1).GetNoDataValue() for band in range(self.nb_band)]
        return self._gdal_dataset.GetRasterBand(1).GetNoDataValue()

    @lazyproperty
    def data_type(self):
        return self._gdal_dataset.GetRasterBand(1).DataType

    @lazyproperty
    def resolution(self):
        """ Return raster X and Y resolution

        """
        return self.geo_transform[1], abs(self.geo_transform[5])

    @lazyproperty
    def std(self):
        """ Compute raster standard deviation for each band

        """
        return [self._gdal_dataset.GetRasterBand(band + 1).ComputeStatistics(False)[3]
                for band in range(self.nb_band)]

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
