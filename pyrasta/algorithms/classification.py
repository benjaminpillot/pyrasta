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


CLASSIFICATION_NO_DATA = -1


def return_classification(classification):
    @wraps(classification)
    def _return_classification(raster, nb_classes, *args, **kwargs):
        with RasterTempFile(raster._gdal_driver.GetMetadata()['DMD_EXTENSION']) as out_file:
            out_ds = _gdal_temp_dataset(out_file.path, raster._gdal_driver,
                                        raster._gdal_dataset.GetProjection(),
                                        raster.x_size, raster.y_size, 1,
                                        raster.geo_transform, gdal.GetDataTypeByName('Int16'),
                                        no_data=CLASSIFICATION_NO_DATA)
            labels = classification(raster, nb_classes, out_ds, *args, **kwargs)

            # Close dataset
            out_ds = None

            new_raster = raster.__class__(out_file.path)
            new_raster._temp_file = out_file

        return new_raster
    return _return_classification


@return_classification
def _k_means_classification(raster, nb_clusters, out_ds, *args, **kwargs):
    """ Apply k-means classification

    """
    k_means_classifier = KMeans(nb_clusters, *args, **kwargs)
    samples = np.reshape(raster._gdal_dataset.ReadAsArray(),
                         (raster.nb_band, raster.x_size * raster.y_size)).transpose()
    labels = k_means_classifier.fit(samples).labels_
    labels = np.reshape(labels, (raster.y_size, raster.x_size))

    out_ds.GetRasterBand(1).WriteArray(labels)


def k_means(raster, nb_clusters, *args, **kwargs):
    """ Compute k-means on given raster

    Description
    -----------
    Run k-means algorithm on raster data

    Warning
    -------
    As the algorithm requires to process all data, all values
    are written to memory. Be sure your machine has enough memory to run it.

    Parameters
    ----------
    raster
    nb_clusters
    args, kwargs :
        sklearn.cluster.KMeans arguments and keyword arguments
        (see scikit-learn documentation)

    Returns
    -------

    """
    _k_means_classification(raster, nb_clusters, *args, **kwargs)
