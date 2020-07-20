# -*- coding: utf-8 -*-

""" Module summary description.

More detailed description.
"""

__author__ = 'Benjamin Pillot'
__copyright__ = 'Copyright 2020, Benjamin Pillot'
__email__ = 'benjaminpillot@riseup.net'


from numba import jit, float32, uint8


def emissivity(window):
    return emissivity_numba(window)


@jit(nopython=True, nogil=True)
def emissivity_numba(window):
    window = window.ravel()
    v_part = window[(window == 4) | (window == 6)].size / window.size
    b_part = window[window < 4].size / window.size
    w_part = window[window == 5].size / window.size

    return 0.004 * v_part ** 2 + 0.986 * v_part - 0.687 * b_part ** 2 + b_part * 0.994 + 0.985 * w_part


if __name__ == "__main__":
    from pyraster.raster import Raster

    test = Raster("/home/benjamin/Documents/classification_brasilia/Classifications_fusion.tif")

    m = test.windowing(emissivity, 11, 'moving', nb_processes=6)

    m.to_file("/home/benjamin/Documents/classification_brasilia/emissivity.tif")
