# -*- coding: utf-8 -*-

""" Module summary description.

More detailed description.
"""

__version__ = '1.3.21'
__author__ = 'Benjamin Pillot'
__email__ = 'benjaminpillot@riseup.net'


try:
    from osgeo import gdal
except ImportError:
    import gdal

GDAL_DEFAULT_DRIVER = gdal.GetDriverByName("Gtiff")
