# PyRasta

[![PyPi license](https://img.shields.io/pypi/l/pyrasta)](https://pypi.python.org/pypi/pyrasta/)
[![Maintenance](https://img.shields.io/badge/Maintained%3F-yes-green.svg)](https://framagit.org/benjaminpillot/pyrasta/activity)
[![PyPI version fury.io](https://badge.fury.io/py/pyrasta.svg)](https://pypi.python.org/pypi/pyrasta/)

Some tools for fast and easy raster processing, based on gdal (numpy usage is reduced to the minimum).

## Introduction
PyRasta is a small Python library which aims at interfacing gdal functions and methods in an easy 
way, so that users may only focus on the processes they want to apply rather than on the code. The
library is based on gdal stream and multiprocessing in order to reduce CPU time due to large numpy 
array imports. This is especially useful for basic raster arithmetic operations, sliding window 
methods as well as zonal statistics.

## Basic available operations
* [x] Merging, clipping, re-projecting, padding, resampling, rescaling, windowing
* [x] Rasterize and Polygonize
* [x] Raster calculator to design your own operations
* [x] Fast raster zonal statistics
* [x] Automatically download and merge SRTM DEM(s) from CGIAR online database

## Install
Pip installation should normally take care of everything for you.

### Using PIP

The easiest way to install PyRasta is by using ``pip`` in a terminal
```
$ pip install pyrasta
```

## Examples

### Build digital elevation model from CGIAR SRTM site
```python
from pyrasta.tools.srtm import from_cgiar_online_database
bounds = (23, 34, 32, 45)
dem = from_cgiar_online_database(bounds)
```

### Fast clipping of raster by extent or by mask
```python
from pyrasta.raster import Raster
import geopandas
raster_by_extent = Raster("/path/to/your/raster").clip(bounds=(10, 40, 15, 45))
raster_by_mask = Raster("/path/to/your/raster").clip(mask=geopandas.GeoDataFrame.from_file("/path/to/your/layer"))
```

### Fast Zonal Statistics
Fast computing of raster zonal statistics within features of a given geographic layer, 
by loading in memory only the data we need (and not the whole numpy array as it is often 
the case in other packages) + using multiprocessing. You may use the basic
statistic functions already available in the package, or define your own customized functions.
```python

from pyrasta.raster import Raster
import geopandas
rstats = Raster("/path/to/your/raster").zonal_stats(geopandas.GeoDataFrame.from_file("/path/to/your/layer"),
                                                    stats=["mean", "median", "min", "max"],
                                                    customized_stats={"my_stat": my_stat})

```

## Author
Benjamin Pillot

<br/>

![image](docs/espace-dev-ird.png)