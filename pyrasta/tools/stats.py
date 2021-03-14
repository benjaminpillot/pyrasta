# -*- coding: utf-8 -*-

""" Module summary description.

More detailed description.
"""

import multiprocessing as mp
from functools import partial
from itertools import tee

import numpy as np
from tqdm import tqdm


STATISTIC_FUNC = dict(median=np.median,
                      mean=np.mean,
                      min=np.min,
                      max=np.max,
                      sum=np.sum)


def _histogram(raster, nb_bins, normalized):
    """ Compute histogram of raster values

    """
    histogram = []

    for band in range(raster.nb_band):
        edges = np.linspace(raster.min, raster.max, nb_bins + 1)
        hist_x = edges[0:-1] + (edges[1::] - edges[0:-1])/2
        hist_y = np.asarray(
            raster._gdal_dataset.GetRasterBand(band + 1).GetHistogram(min=raster.min[band],
                                                                      max=raster.max[band],
                                                                      buckets=nb_bins))
        if normalized:
            hist_y = hist_y / np.sum(hist_y)

        histogram.append((hist_x, hist_y))

    return histogram


def _zonal_stats(raster, layer, band, stats, customized_stat,
                 no_data, all_touched, show_progressbar, nb_processes):
    """ Retrieve zonal statistics from raster corresponding to features in layer
    
    Parameters
    ----------
    raster: RasterBase
        Raster from which zonal statistics must be computed
    layer: geopandas.GeoDataFrame or gistools.layer.GeoLayer
        Geographic layer as a GeoDataFrame or GeoLayer
    band: int
        band number
    stats: list[str]
        list of strings of valid available statistics:
        - 'mean' returns average over the values within each zone
        - 'median' returns median
        - 'sum' returns the sum of all values in zone
        - 'min' returns minimum value
        - 'max' returns maximum value
    customized_stat: dict
        User's own customized statistic function
        as {'your_function_name': function}
    no_data: int or float
        No data value
    all_touched: bool
        Whether to include every raster cell touched by a geometry, or only
        those having a center point within the polygon.
    show_progressbar: bool
        if True, show progress bar status
    nb_processes: int
        Number of parallel processes

    Returns
    -------

    """
    stats_calc = {name: STATISTIC_FUNC[name] for name in stats}
    if customized_stat is not None:
        stats_calc.update(customized_stat)

    layer["ID"] = layer.index
    raster_layer = raster.rasterize(layer, raster.projection, raster.x_size,
                                    raster.y_size, raster.geo_transform,
                                    attribute="ID", all_touched=all_touched)

    bounds = layer.bounds.to_numpy()
    zone = (raster.read_array(band, boundary) for boundary in bounds)
    zone_id = (raster_layer.read_array(bounds=boundary) for boundary in bounds)
    multi_gen = tee(zip(layer.index, zone, zone_id), len(stats_calc))

    if show_progressbar:
        iterator = tqdm(zip(multi_gen, stats_calc.keys()),
                        desc="Compute zonal statistics",
                        total=len(stats_calc))
    else:
        iterator = zip(multi_gen, stats_calc.keys())

    output = dict()
    with mp.Pool(processes=nb_processes) as pool:
        for generator, name in iterator:
            output[name] = list(pool.starmap(partial(_compute_stat_in_feature,
                                                     no_data=raster.no_data,
                                                     stat_function=stats_calc[name]),
                                             generator))

    return output


def _compute_stat_in_feature(idx, zone, zone_id, no_data, stat_function):

    values = zone[(zone_id == idx) & (zone != no_data)]

    if values.size != 0:
        return stat_function(values)
    else:
        return np.nan
