# -*- coding: utf-8 -*-

""" Module summary description.

More detailed description.
"""

import numpy as np


def _histogram(raster, nb_bins, normalized):
    """ Compute histogram of raster values

    """
    histogram = []

    for band in range(raster.nb_band):
        edges = np.linspace(raster.min, raster.max, nb_bins + 1)
        hist_x = edges[0:-1] + (edges[1::] - edges[0:-1])/2
        hist_y = np.asarray(raster._gdal_dataset.GetRasterBand(band + 1).GetHistogram(min=raster.min[band],
                                                                                      max=raster.max[band],
                                                                                      buckets=nb_bins))
        if normalized:
            hist_y = hist_y / np.sum(hist_y)

        histogram.append((hist_x, hist_y))

    return histogram
