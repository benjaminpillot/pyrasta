# -*- coding: utf-8 -*-

""" Digital Elevation Model functions

More detailed description.
"""
from pyrasta.tools import _return_raster

try:
    from osgeo import gdal
except ImportError:
    import gdal


@_return_raster
def _slope(dem, out_file, slope_format, scale):
    """ Compute DEM slope

    Parameters
    ----------
    dem: pyrasta.raster.DigitalElevationModel
    out_file: str
        output file path to which new dem must be written
    slope_format: str
        Slope format {'percent', 'degree'}

    Returns
    -------

    """
    options = gdal.DEMProcessingOptions(format=dem._gdal_driver.ShortName,
                                        slopeFormat=slope_format,
                                        scale=scale)
    gdal.DEMProcessing(out_file, dem._gdal_dataset, 'slope', options=options)


@_return_raster
def _aspect(dem, out_file, scale):
    """ Compute aspect

    Parameters
    ----------
    dem
    out_file
    scale

    Returns
    -------

    """
    options = gdal.DEMProcessingOptions(format=dem._gdal_driver.ShortName,
                                        scale=scale)
    gdal.DEMProcessing(out_file, dem._gdal_dataset, "aspect", options=options)
