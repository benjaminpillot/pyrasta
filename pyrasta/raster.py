# -*- coding: utf-8 -*-

""" Module summary description.

More detailed description.
"""

from pyrasta.base import RasterBase
from pyrasta.tools.dem import _slope, _aspect


class Raster(RasterBase):
    pass


class DigitalElevationModel(Raster):

    def aspect(self, scale=1):
        """ Compute DEM aspect

        Parameters
        ----------
        scale: float or int
            Ratio of vertical units to horizontal

        Returns
        -------

        """
        return _aspect(self, scale)

    def slope(self, slope_format="percent", scale=1):
        """ Compute DEM slope

        Parameters
        ----------
        slope_format: str
            Slope format {'percent', 'degree'}
        scale: int or float
            Ratio of vertical units to horizontal

        Returns
        -------

        """
        return _slope(self, slope_format, scale)
