# -*- coding: utf-8 -*-

""" Module summary description.

More detailed description.
"""
import numpy as np
import osmnx as ox
from gistools.layer import PolygonLayer
from matplotlib import pyplot

from pyrasta.raster import DigitalElevationModel, Raster
from pyrasta.tools.clip import _clip_raster_by_mask
from pyrasta.tools.rasterize import _rasterize
from pyrasta.tools.srtm import from_cgiar_online_database

# bounds = (5, 40, 10, 45)
# test = from_cgiar_online_database(bounds)
# test.to_file("/home/benjamin/srtm_corse.tif")

# test = DigitalElevationModel("/home/benjamin/dem_test.tif").clip((13, 42, 15, 45)).to_file(
#     "/home/benjamin/dem_clip_test.tif")
# pop = Raster("/home/benjamin/Documents/PRO/PRODUITS/POPULATION_DENSITY/001_DONNEES/COTE_D_IVOIRE"
#              "/population_civ_2019-07-01_geotiff/population_civ_2019-07-01.tif")
from pyrasta.tools.stats import _zonal_stats

dem = DigitalElevationModel("/home/benjamin/Documents/PRO/PRODUITS/TESTS/dem_ci.tif")
country = PolygonLayer.from_gpd(ox.geocode_to_gdf(
    dict(country="Cote d'Ivoire",
         admin_level=2,
         type="boundary"))).to_crs(32630).clean_geometry()

# dem = from_cgiar_online_database(country.total_bounds)
# dem.to_file("/home/benjamin/dem_ci.tif")

honeycomb = country.split(country.area[0] / 100, method="hexana", show_progressbar=True)

honeycomb = honeycomb.to_crs(dem.crs)
honeycomb.to_file("/home/benjamin/Documents/PRO/PRODUITS/TESTS/honeycomb.shp")
honeycomb["ID"] = honeycomb.index

# test = dem.clip(mask=honeycomb[[15]], all_touched=True)
# test.to_file("/home/benjamin/pop.tif")

# test = dem.zonal_stats(honeycomb, stats=["mean", "median"])

# test = dem.rasterize(honeycomb, dem.projection, dem.x_size, dem.y_size, dem.geo_transform,
#                      attribute="ID", nb_band=1)
# test = _rasterize(DigitalElevationModel, honeycomb, None, "ID", dem._gdal_driver,
#                   dem._gdal_dataset.GetProjection(),
#                   dem.x_size, dem.y_size, 1, dem.geo_transform, dem.data_type, -999, True)
# test = DigitalElevationModel(test.path)
# test.to_file("/home/benjamin/test_ci.tif")

stats = _zonal_stats(dem, honeycomb, 1, ['mean', 'median', 'max', 'min'], dict(mymax=np.max), -999,
                     True, True, 6)

print(stats.keys())
print("mymax: %s" % stats["mymax"])
print(len(honeycomb))
