# -*- coding: utf-8 -*-

""" Module summary description.

More detailed description.
"""

import multiprocessing as mp
from functools import partial
from itertools import tee

import numpy as np
from tqdm import tqdm


STATISTIC_FUNC = dict(count=np.size,
                      median=np.median,
                      mean=np.mean,
                      min=np.min,
                      max=np.max,
                      std=np.std,
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
                 all_touched, show_progressbar, nb_processes):
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
        - 'count' returns number of valid values in zone
        - 'mean' returns average over the values within each zone
        - 'median' returns median
        - 'sum' returns the sum of all values in zone
        - 'std' returns std of all values in zone
        - 'min' returns minimum value
        - 'max' returns maximum value
    customized_stat: dict
        User's own customized statistic function
        as {'your_function_name': function}
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
    def zone_gen(ras, bds, bd=1):
        for boundary in bds:
            try:
                yield ras.read_array(bd, boundary)
            except RuntimeError:
                yield None

    try:
        stats_calc = {name: STATISTIC_FUNC[name] for name in stats}
    except TypeError:
        stats_calc = {}

    try:
        stats_calc.update(customized_stat)
    except TypeError:
        pass

    layer["__ID__"] = layer.index
    raster_layer = raster.rasterize(layer, raster.projection, raster.x_size,
                                    raster.y_size, raster.geo_transform,
                                    attribute="__ID__", all_touched=all_touched)

    bounds = layer.bounds.to_numpy()
    zone = zone_gen(raster, bounds, band)
    zone_id = zone_gen(raster_layer, bounds)
    multi_gen = tee(zip(layer.index, zone, zone_id), len(stats_calc))

    iterator = zip(multi_gen, stats_calc.keys())

    output = dict()
    with mp.Pool(processes=nb_processes) as pool:
        if show_progressbar:
            for generator, name in iterator:
                output[name] = list(tqdm(pool.starmap(partial(_compute_stat_in_feature,
                                                              no_data=raster.no_data,
                                                              stat_function=stats_calc[name]),
                                                      generator),
                                         total=len(layer),
                                         unit_scale=True,
                                         desc=f"Compute zonal {name}"))
        else:
            for generator, name in iterator:
                output[name] = list(pool.starmap(partial(_compute_stat_in_feature,
                                                         no_data=raster.no_data,
                                                         stat_function=stats_calc[name]),
                                                 generator))

    return output


def _compute_stat_in_feature(idx, zone, zone_id, no_data, stat_function):

    if zone is not None and zone_id is not None:
        if np.isnan(no_data):
            values = zone[(zone_id == idx) & ~np.isnan(zone)]
        else:
            values = zone[(zone_id == idx) & (zone != no_data)]

        if values.size != 0:
            return stat_function(values)
        else:
            return np.nan
    else:
        return np.nan
