# -*- coding: utf-8 -*-

""" Module summary description.

More detailed description.
"""

from functools import wraps

import numpy as np
from pyrasta.io_.files import RasterTempFile
from pyrasta.tools import _gdal_temp_dataset
from sklearn.cluster import KMeans

import gdal


def return_classification(classification):
    @wraps(classification)
    def _return_classification(raster, nb_classes, *args, **kwargs):
        with RasterTempFile(raster._gdal_driver.GetMetadata()['DMD_EXTENSION']) as out_file:
            out_ds = _gdal_temp_dataset(out_file.path, raster._gdal_driver,
                                        raster._gdal_dataset.GetProjection(),
                                        raster.x_size, raster.y_size, 1,
                                        raster.geo_transform, gdal.GetDataTypeByName('Int16'),
                                        no_data=-999)
            labels = classification(raster, nb_classes, out_ds, *args, **kwargs)

            # Close dataset
            out_ds = None

            new_raster = raster.__class__(out_file.path)
            new_raster._temp_file = out_file

        return new_raster
    return _return_classification


@return_classification
def _k_means_classification(raster, nb_clusters, out_ds, n_init, max_iter):
    """ Apply k-means classification

    """
    k_means_classifier = KMeans(nb_clusters, n_init=n_init, max_iter=max_iter)
    values = np.reshape(raster._gdal_dataset.ReadAsArray(),
                        (raster.nb_band, raster.x_size * raster.y_size)).transpose()
    labels = np.reshape(k_means_classifier.fit(values).labels_, (raster.y_size, raster.x_size))

    out_ds.GetRasterBand(1).WriteArray(labels)


def k_means_classification(raster, nb_clusters, n_init=100, max_iter=1000):
    _k_means_classification(raster, nb_clusters, n_init, max_iter)
