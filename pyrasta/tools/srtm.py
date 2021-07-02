# -*- coding: utf-8 -*-

""" Module summary description.

More detailed description.
"""
from zipfile import ZipFile
from urllib.error import URLError
from urllib.request import urlretrieve
import tempfile
import os

from tqdm import tqdm

from pyrasta.raster import DigitalElevationModel
from pyrasta.utils import digitize, TqdmUpTo


CGIAR_ARCHIVE_FORMAT = "zip"
CGIAR_URL = "http://srtm.csi.cgiar.org/wp-content/uploads/files/srtm_5x5/TIFF"
CGIAR_NO_DATA = -32768
CGIAR_DATA_TYPE = 3


def _download_srtm_tile(tile_name):
    """ Download and extract SRTM tile archive

    Description
    -----------

    Parameters
    ----------
    tile_name: str
        SRTM tile name
    """
    zip_name, tif_name = tile_name + "." + CGIAR_ARCHIVE_FORMAT, tile_name + '.tif'
    url = os.path.join(CGIAR_URL, zip_name)
    temp_srtm_zip = os.path.join(tempfile.gettempdir(), zip_name)
    temp_srtm_dir = os.path.join(tempfile.gettempdir(), tile_name)

    # Download tile
    try:
        with TqdmUpTo(unit='B', unit_scale=True, unit_divisor=1024, miniters=1,
                      desc=zip_name) as t:
            urlretrieve(url, temp_srtm_zip, reporthook=t.update_to)
            t.total = t.n
    except URLError as e:
        raise RuntimeError("Unable to fetch data at '%s': %s" % (url, e))

    # Extract GeoTiff
    # In order to avoid conflict with the archive extraction,
    # the "gdal import" is located at the end of all the imports
    # See https://github.com/conda-forge/gdal-feedstock/issues/365
    with ZipFile(temp_srtm_zip, 'r') as archive:
        archive.extractall(temp_srtm_dir)

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
    x_min = digitize(bounds[0], srtm_lon, right=False)
    x_max = digitize(bounds[2], srtm_lon, right=True)
    y_min = digitize(bounds[3], srtm_lat, right=True, ascend=False)
    y_max = digitize(bounds[1], srtm_lat, right=False, ascend=False)

    list_of_tiles = []

    coords = [(x, y) for x in range(int(x_min), int(x_max) + 1)
              for y in range(int(y_min), int(y_max) + 1)]

    for (x, y) in tqdm(coords, desc="Downloading SRTM tile(s)"):
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
    tiles = [DigitalElevationModel(tile) for tile in _retrieve_cgiar_srtm_tiles(bounds)]

    return DigitalElevationModel.merge(tiles,
                                       bounds,
                                       data_type=CGIAR_DATA_TYPE,
                                       no_data=CGIAR_NO_DATA)
