# -*- coding: utf-8 -*-

""" Module summary description.

More detailed description.
"""

__author__ = 'Benjamin Pillot'
__copyright__ = 'Copyright 2020, Benjamin Pillot'
__email__ = 'benjaminpillot@riseup.net'

import os
import tempfile
from urllib.error import URLError
from urllib.request import urlretrieve
from zipfile import ZipFile

from pyraster import INT32
from pyraster.raster import DigitalElevationModel
from pyraster.utils import digitize, TqdmUpTo


CGIAR_URL = "http://srtm.csi.cgiar.org/wp-content/uploads/files/srtm_5x5/TIFF"
CGIAR_NO_DATA = -32768
CGIAR_DATA_TYPE = INT32


def _download_srtm_tile(tile_name):
    """ Download and extract SRTM tile archive

    Description
    -----------

    Parameters
    ----------
    tile_name: str
        SRTM tile name
    """
    zip_name, tif_name = tile_name + ".zip", tile_name + '.tif'
    url = os.path.join(CGIAR_URL, zip_name)
    temp_srtm_zip = os.path.join(tempfile.gettempdir(), zip_name)
    temp_srtm_dir = os.path.join(tempfile.gettempdir(), tile_name)

    # Download tile
    try:
        with TqdmUpTo(unit='B', unit_scale=True, unit_divisor=1024, miniters=1,
                      desc=zip_name + ' ') as t:
            urlretrieve(url, temp_srtm_zip, reporthook=t.update_to)
            t.total = t.n
    except URLError as e:
        raise RuntimeError("Unable to fetch data at '%s': %s" % (url, e))

    # Extract GeoTiff
    archive = ZipFile(temp_srtm_zip, 'r')
    archive.extractall(temp_srtm_dir)
    archive.close()

    return os.path.join(temp_srtm_dir, tif_name)


def _retrieve_cgiar_srtm_tiles(bounds):
    """ Import DEM tile from CGIAR-CSI SRTM3 database (V4.1)

    Description
    -----------

    Parameters
    ----------
    bounds: tuple or list
        output DEM bounds as (x_min, y_min, x_max, y_max)

    Returns
    -------
    list:
        list of SRTM tile file names

    """
    srtm_lon = range(-180, 185, 5)
    srtm_lat = range(60, -65, -5)
    x_min, x_max = digitize(bounds[0], srtm_lon, right=True), digitize(bounds[2], srtm_lon, right=True)
    y_min, y_max = digitize(bounds[3], srtm_lat, ascend=False), digitize(bounds[1], srtm_lat, ascend=False)

    list_of_tiles = []

    for x in range(int(x_min), int(x_max) + 1):
        for y in range(int(y_min), int(y_max) + 1):
            tile = _download_srtm_tile("srtm_%02d_%02d" % (x, y))
            list_of_tiles.append(tile)

    return list_of_tiles


def from_cgiar_online_database(bounds):
    """ Build DEM tile from CGIAR-CSI SRTM3 database (V4.1)

    Description
    -----------

    Parameters
    ----------
    bounds: tuple or list
        output DEM bounds

    Returns
    -------
    DigitalElevationModel:
        new instance

    """
    list_of_tiles = [DigitalElevationModel(tile, no_data=CGIAR_NO_DATA)
                     for tile in _retrieve_cgiar_srtm_tiles(bounds)]

    return DigitalElevationModel.merge(list_of_tiles, bounds, data_type=CGIAR_DATA_TYPE)
