# -*- coding: utf-8 -*-

""" Module summary description.

More detailed description.
"""
import gdal
from pyrasta.tools import _clone_gdal_dataset, _return_raster
from pyrasta.utils import gdal_progress_bar


@_return_raster
def _sieve(raster, out_file, threshold, connectedness, progress_bar):
    """ Apply sieve filter to raster

    Parameters
    ----------
    raster
    out_file
    threshold: int
    connectedness: int
    progress_bar: bool

    Returns
    -------

    """
    out_ds = _clone_gdal_dataset(raster, out_file)

    callback, callback_data = gdal_progress_bar(progress_bar,
                                                description="Apply sieve filter")

    for band in range(raster.nb_band):
        gdal.SieveFilter(raster._gdal_dataset.GetRasterBand(band + 1),
                         None,
                         out_ds.GetRasterBand(band + 1),
                         threshold,
                         connectedness,
                         callback=callback,
                         callback_data=callback_data)

    # Close dataset
    out_ds = None
