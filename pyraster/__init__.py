# -*- coding: utf-8 -*-

""" Module summary description.

More detailed description.
"""

__version__ = '1.0'
__author__ = 'Benjamin Pillot'
__copyright__ = 'Copyright 2020, Benjamin Pillot'
__email__ = 'benjaminpillot@riseup.net'

import gdal
import osr

gdal.UseExceptions()
osr.UseExceptions()

FLOAT32 = gdal.GetDataTypeByName('Float32')
FLOAT64 = gdal.GetDataTypeByName('Float64')
INT16 = gdal.GetDataTypeByName('Int16')
INT32 = gdal.GetDataTypeByName('Int32')
UINT16 = gdal.GetDataTypeByName('Uint16')
UINT32 = gdal.GetDataTypeByName('Uint32')

GTIFF_DRIVER = gdal.GetDriverByName('Gtiff')
