# -*- coding: utf-8 -*-

""" Module summary description.

More detailed description.
"""

__author__ = 'Benjamin Pillot'
__copyright__ = 'Copyright 2020, Benjamin Pillot'
__email__ = 'benjaminpillot@riseup.net'

from pyraster.tools.srtm import from_cgiar_online_database

bounds = (9, 40, 10, 42)
test = from_cgiar_online_database(bounds)
test.to_file("/home/benjamin/dem_test.tif")
