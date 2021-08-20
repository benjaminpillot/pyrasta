# -*- coding: utf-8 -*-

""" Functions related to CRS conversion and computation

More detailed description.
"""

try:
    from osgeo import osr
except ImportError:
    import osr

import pyproj


def is_equal_proj(proj1, proj2):
    """ Compare 2 projections

    Parameters
    ----------
    proj1: int or str or dict or pyproj.Proj
        valid projection name
    proj2: int or str or dict or pyproj.Proj
        valid projection name

    Returns
    -------
    boolean:
        True or False
    """
    # From an idea from https://github.com/jswhit/pyproj/issues/15
    # Use OGR library to compare projections
    srs = [srs_from(proj1), srs_from(proj2)]

    return bool(srs[0].IsSame(srs[1]))


def proj4_from_wkt(wkt):
    """ Convert wkt srs to proj4

    Description
    -----------

    Parameters
    ----------
    wkt:

    Returns
    -------

    """
    srs = osr.SpatialReference()
    srs.ImportFromWkt(wkt)

    return srs.ExportToProj4()


def proj4_from(proj):
    """ Convert projection to proj4 string

    Description
    -----------
    Convert projection string, dictionary, etc.
    to proj4 string

    Parameters
    ----------
    proj:

    Returns
    -------

    """
    if type(proj) == int:
        try:
            proj4_str = pyproj.Proj('epsg:%d' % proj).srs
        except (ValueError, RuntimeError):
            raise ValueError("Invalid EPSG code")
    elif type(proj) == str or type(proj) == dict:
        try:
            proj4_str = pyproj.Proj(proj).srs
        except RuntimeError:
            try:
                proj4_str = proj4_from_wkt(proj)
            except (RuntimeError, TypeError):
                raise ValueError("Invalid projection string or dictionary")
    elif type(proj) == pyproj.Proj:
        proj4_str = proj.srs
    else:
        raise ValueError("Invalid projection format: '{}'".format(type(proj)))

    return proj4_str


def srs_from(crs):
    """ Get spatial reference system from projection

    Description
    -----------

    Parameters
    ----------
    crs:

    Returns
    -------
    SpatialReference instance (osgeo.osr package)
    """
    # proj4 = proj4_from(proj)
    srs = osr.SpatialReference()
    srs.ImportFromWkt(crs.to_wkt())

    return srs
