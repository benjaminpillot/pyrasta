# -*- coding: utf-8 -*-

""" Module summary description.

More detailed description.
"""

import multiprocessing as mp

import numpy as np
import ogr
import pyproj
from pyrasta.io_.files import _copy_to_file
from pyrasta.tools.calculator import _op, _raster_calculation, _log, _log10
from pyrasta.tools.clip import _clip_raster_by_extent, _clip_raster_by_mask
from pyrasta.tools.conversion import _resample_raster, _padding, _rescale_raster, \
    _align_raster, _extract_bands, _merge_bands, _read_array, _xy_to_2d_index, _read_value_at, \
    _project_raster, _array_to_raster, _set_no_data, _set_data_type
from pyrasta.exceptions import RasterBaseError
from pyrasta.tools.filters import _sieve
from pyrasta.tools.mask import _raster_mask
from pyrasta.tools.merge import _merge
from pyrasta.tools.polygonize import _polygonize
from pyrasta.tools.rasterize import _rasterize
from pyrasta.tools.stats import _histogram, _zonal_stats
from pyrasta.tools.windows import _windowing
from pyrasta.utils import lazyproperty, grid, MP_CHUNK_SIZE

import gdal

gdal.UseExceptions()


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

        # If NoData not defined, define here
        # for band in range(self.nb_band):
        #     if no_data is not None:
        #         if self._gdal_dataset.GetRasterBand(band + 1).GetNoDataValue() is None:
        #             self._gdal_dataset.GetRasterBand(band + 1).SetNoDataValue(no_data)
        #         else:
        #             warnings.warn("No data value is already set, cannot overwrite.")

        self._gdal_driver = self._gdal_dataset.GetDriver()
        self._file = src_file

    def __add__(self, other):
        return _op(self, other, "add")

    def __sub__(self, other):
        return _op(self, other, "sub")

    def __mul__(self, other):
        return _op(self, other, "mul")

    def __pow__(self, other):
        return _op(self, other, "pow")

    def __radd__(self, other):

        return _op(self, other, 'add')

    def __rmul__(self, other):

        return _op(self, other, "mul")

    def __rpow__(self, other):

        return _op(self, other, "rpow")

    def __rsub__(self, other):

        return _op(self, other, 'rsub')

    def __rtruediv__(self, other):

        return _op(self, other, "rtruediv")

    def __truediv__(self, other):
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

    def clip(self, bounds=None, mask=None, no_data=-999, all_touched=True):
        """ Clip raster

        Parameters
        ----------
        bounds: tuple
            tuple (x_min, y_min, x_max, y_max) in map units
        mask: geopandas.GeoDataFrame
            Valid mask layer
        no_data: int or float
            No data value
        all_touched: bool
            if True, all touched pixels within layer boundaries are burnt,
            when clipping raster by mask

        Returns
        -------
        RasterBase:
            New temporary instance

        """
        if bounds is not None:
            return _clip_raster_by_extent(self, bounds, no_data)
        elif mask is not None:
            return _clip_raster_by_mask(self, mask, no_data, all_touched)
        else:
            raise ValueError("Either bounds or mask must be set")

    def extract_bands(self, bands):
        """ Extract bands as multiple rasters

        Description
        -----------

        Parameters
        ----------
        bands: list
            list of band numbers

        Returns
        -------
        """
        return _extract_bands(self, bands)

    @classmethod
    def from_array(cls, array, crs, bounds,
                   gdal_driver=gdal.GetDriverByName("Gtiff"),
                   no_data=-999):

        return _array_to_raster(cls, array, crs, bounds, gdal_driver, no_data)

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

    def log(self):
        """ Return logarithm of raster data

        Returns
        -------

        """
        return _log(self)

    def log10(self):
        """ Return base 10 logarithm

        Returns
        -------

        """
        return _log10(self)

    def mask(self, mask, gdal_driver=gdal.GetDriverByName("Gtiff"),
             data_type=gdal.GetDataTypeByName('Float32'),
             all_touched=True, no_data=-999, window_size=500):
        """ Apply mask to raster

        Parameters
        ----------
        mask: geopandas.geodataframe or gistools.layer.GeoLayer
            Mask layer as a GeoDataFrame or GeoLayer
        gdal_driver: osgeo.gdal.Driver
            Driver used to write data to file
        data_type: int
            GDAL data type
        all_touched: bool
            if True, all touched pixels within layer boundaries are burnt,
            when clipping raster by mask
        no_data: int or float
            output no data value in masked raster
        window_size: int or list[int, int]
            Size of window for raster calculation

        Returns
        -------

        """
        return _raster_mask(self, mask, gdal_driver, data_type,
                            no_data, all_touched, window_size)

    @classmethod
    def merge(cls, rasters, bounds=None,
              gdal_driver=gdal.GetDriverByName("Gtiff"),
              data_type=gdal.GetDataTypeByName('Float32'), no_data=-999):
        """ Merge multiple rasters

        Description
        -----------

        Parameters
        ----------
        rasters: Collection
            Collection of RasterBase instances
        bounds: tuple
            bounds of the new merged raster
        gdal_driver
        data_type: int
            GDAL data type
        no_data: int or float
            output no data value in merged raster

        Returns
        -------

        """
        return _merge(cls, rasters, gdal_driver, bounds, data_type, no_data)

    @classmethod
    def merge_bands(cls, rasters, resolution="highest",
                    gdal_driver=gdal.GetDriverByName("Gtiff"),
                    data_type=gdal.GetDataTypeByName('Float32'),
                    no_data=-999):
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
        gdal_driver: gdal.Driver
        data_type: int
            GDAL data type
        no_data: int or float
            no data value in output raster
        """
        return _merge_bands(cls, rasters, resolution, gdal_driver, data_type, no_data)

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

    def polygonize(self, filename, band=1, layer_name="layer", field_name="unknown",
                   ogr_driver=ogr.GetDriverByName("ESRI Shapefile"),
                   is_8_connected=False, progress_bar=False):
        """ Polygonize raster

        Parameters
        ----------
        filename: str
        band: int
        layer_name: str
        field_name: str
        ogr_driver: ogr.Driver
        is_8_connected: bool
        progress_bar: bool

        Returns
        -------

        """
        return _polygonize(self, filename, band, layer_name,
                           field_name, ogr_driver, is_8_connected,
                           progress_bar)

    @classmethod
    def rasterize(cls, layer, projection, x_size, y_size, geo_transform,
                  burn_values=None, attribute=None,
                  gdal_driver=gdal.GetDriverByName("Gtiff"), nb_band=1,
                  data_type=gdal.GetDataTypeByName("Float32"), no_data=-999,
                  all_touched=True, progress_bar=False):
        """ Rasterize geographic layer

        Parameters
        ----------
        layer: geopandas.GeoDataFrame or gistools.layer.GeoLayer
            Geographic layer to be rasterized
        projection: str
            Projection as a WKT string
        x_size: int
            Raster width
        y_size: int
            Raster height
        geo_transform: tuple
        burn_values: list[float] or list[int], default None
            List of values to be burnt in each band, excusive with attribute
        attribute: str, default None
            Layer's attribute to be used for values to be burnt in raster,
            excusive with burn_values
        gdal_driver: osgeo.gdal.Driver, default GeoTiff
            GDAL driver
        nb_band: int, default 1
            Number of bands
        data_type: int, default "Float32"
            GDAL data type
        no_data: int or float, default -999
            No data value
        all_touched: bool
        progress_bar: bool
            Is progress bar displayed ?

        Returns
        -------

        """
        return _rasterize(cls, layer, burn_values, attribute, gdal_driver, projection,
                          x_size, y_size, nb_band, geo_transform, data_type, no_data,
                          all_touched, progress_bar)

    @classmethod
    def raster_calculation(cls, rasters, fhandle, window_size=100,
                           gdal_driver=gdal.GetDriverByName("Gtiff"),
                           input_type=gdal.GetDataTypeByName('Float32'),
                           output_type=gdal.GetDataTypeByName('Float32'),
                           no_data=-999, nb_processes=mp.cpu_count(),
                           chunksize=MP_CHUNK_SIZE,
                           description="Calculate raster expression"):
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
            expression to calculate (must accept a collection of arrays)
        window_size: int or (int, int)
            size of window/chunk to set in memory during calculation
            * unique value
            * tuple of 2D coordinates (width, height)
        gdal_driver: osgeo.gdal.Driver
            GDAL driver (output format)
        input_type: int
            GDAL data type for input raster (if multiple types, let "float32")
        output_type: int
            GDAL data type for output raster
        no_data: int or float
            no data value in resulting raster
        nb_processes: int
            number of processes for multiprocessing pool
        chunksize: int
            chunk size used in map/imap multiprocessing function
        description: str
            Progress bar description. If None, no progress bar is displayed

        Returns
        -------
        RasterBase
            New temporary instance
        """
        return _raster_calculation(cls, rasters, fhandle, window_size,
                                   gdal_driver, input_type, output_type,
                                   no_data, nb_processes, chunksize, description)

    def read_array(self, band=None, bounds=None):
        """ Write raster to numpy array

        Parameters
        ----------
        band: int
            Band number. If None, read all bands into multidimensional array.
        bounds: tuple
            tuple as (x_min, y_min, x_max, y_max) in map units. If None, read
            the whole raster into array

        Returns
        -------
        numpy.ndarray

        """
        return _read_array(self, band, bounds)

    def read_value_at(self, x, y):
        """ Read value in raster at x/y map coordinates

        Parameters
        ----------
        x: float
            lat coordinates in map units
        y: float
            lon coordinates in map units

        Returns
        -------

        """
        return _read_value_at(self, x, y)

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
        RasterBase
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

        Returns
        -------
        """
        return _rescale_raster(self, r_min, r_max)

    def set_no_data(self, no_data):
        """ Set no data value in raster

        Parameters
        ----------
        no_data: int or float

        Returns
        -------
        RasterBase

        """
        return _set_no_data(self, no_data)

    def set_data_type(self, data_type):
        """ Set data type

        Parameters
        ----------
        data_type: str
            Valid GDAL data type name

        Returns
        -------
        RasterBase

        """
        return _set_data_type(self, gdal.GetDataTypeByName(data_type))

    def sieve_filter(self, threshold=1, connectedness=4, progress_bar=False):
        """ Apply sieve filter

        Parameters
        ----------
        threshold: int
        connectedness: int
        progress_bar: bool

        Returns
        -------

        """
        return _sieve(self, threshold, connectedness, progress_bar)

    def to_crs(self, crs):
        """ Re-project raster onto new CRS

        Parameters
        ----------
        crs: int or str or pyproj.CRS
            valid CRS (Valid pyproj CRS, EPSG code, proj string, etc.)

        Returns
        -------

        """
        return _project_raster(self, pyproj.CRS(crs))

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

    def windowing(self, f_handle, window_size, method, band=None,
                  data_type=gdal.GetDataTypeByName('Float32'),
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
        RasterBase
            New instance

        """
        if band is None:
            band = 1

        if no_data is None:
            no_data = self.no_data

        return _windowing(self, f_handle, band, window_size, method,
                          data_type, no_data, chunk_size, nb_processes)

    def xy_to_2d_index(self, x, y):
        """ Convert x/y map coordinates into 2d index

        Parameters
        ----------
        x: float
            x coordinates in map units
        y: float
            y coordinates in map units

        Returns
        -------
        tuple
            (px, py) index

        """
        return _xy_to_2d_index(self, x, y)

    def zonal_stats(self, layer, band=1, stats=None, customized_stats=None,
                    all_touched=True, show_progressbar=True,
                    nb_processes=mp.cpu_count()):
        """ Compute zonal statistics

        Compute statistic among raster values
        within each feature of given geographic layer

        Parameters
        ----------
        layer: geopandas.GeoDataFrame or gistools.layer.GeoLayer
            Geographic layer
        band: int
            Band number
        stats: list[str]
            list of valid statistic names
            "mean", "median", "min", "max", "sum", "std"
        customized_stats: dict
            User's own customized statistic functions
            as {'your_function_name': function}
        all_touched: bool
            Whether to include every raster cell touched by a geometry, or only
            those having a center point within the polygon.
        show_progressbar: bool
            If True, show progress bar status
        nb_processes: int
            number of processes for multiprocessing

        Returns
        -------
        dict[list]
            Dictionary with each statistic as a list corresponding
            to the values for each feature in layer

        """
        if stats is not None:
            return _zonal_stats(self, layer, band, stats, customized_stats,
                                all_touched, show_progressbar, nb_processes)

    @property
    def crs(self):
        """ Return Coordinate Reference System

        """
        return pyproj.CRS(self._gdal_dataset.GetProjection())

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
    def grid_y(self):
        return [lat for lat in grid(self.y_origin + self.geo_transform[5]/2,
                                    self.geo_transform[5], self.y_size)]

    @lazyproperty
    def grid_x(self):
        return [lon for lon in grid(self.x_origin + self.geo_transform[1]/2,
                                    self.geo_transform[1], self.x_size)]

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

    @property
    def no_data(self):
        no_data = self._gdal_dataset.GetRasterBand(1).GetNoDataValue()
        if no_data is None:
            return np.nan
        else:
            return no_data
        # return self._gdal_dataset.GetRasterBand(1).GetNoDataValue()

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
    def projection(self):
        """ Get projection as a WKT string

        """
        return self._gdal_dataset.GetProjection()

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
