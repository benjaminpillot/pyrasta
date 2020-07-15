# -*- coding: utf-8 -*-

""" Module summary description.

More detailed description.
"""
from functools import wraps

from pyraster.tools.conversion import _resample_raster, _padding
from pyraster.tools.merge import _merge
from pyraster.utils import lazyproperty


def return_new_instance(method):
    @wraps(method)
    def _return_new_instance(self, *args, **kwargs):
        output = method(self, *args, **kwargs)
        try:
            new_self = self.__class__(output)
        except RuntimeError:
            return output
    return _return_new_instance


class RasterBase:

    crs = None
    file = None
    gdal_dataset = None
    gdal_driver = None

    rasterio_dataset = None

    def __init__(self):
        pass

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

    @lazyproperty
    def bounds(self):
        return self.rasterio_dataset.bounds

    @lazyproperty
    def nb_band(self):
        return self.gdal_dataset.RasterCount

    @lazyproperty
    def no_data(self):
        return [self.gdal_dataset.GetRasterBand(band + 1).GetNoDataValue() for band in range(self.nb_band)]

    @lazyproperty
    def resolution(self):
        return self.rasterio_dataset.res

    @lazyproperty
    def x_origin(self):
        return self.rasterio_dataset.bounds[0]

    @lazyproperty
    def x_size(self):
        return self.gdal_dataset.RasterXSize

    @lazyproperty
    def y_origin(self):
        return self.rasterio_dataset.bounds[3]

    @lazyproperty
    def y_size(self):
        return self.gdal_dataset.RasterYSize
