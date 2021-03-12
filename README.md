# PyRasta

[![PyPi license](https://img.shields.io/pypi/l/pyrasta)](https://pypi.python.org/pypi/pyrasta/)
[![Maintenance](https://img.shields.io/badge/Maintained%3F-yes-green.svg)](https://framagit.org/benjaminpillot/pyraster/activity)
[![PyPI version fury.io](https://badge.fury.io/py/pyrasta.svg)](https://pypi.python.org/pypi/pyrasta/)

Some tools for fast and easy raster processing, based on gdal (numpy usage is reduced to the minimum).

## Introduction
PyRasta is a small Python library which aims at interfacing gdal functions and methods in an easy 
way, so that users may only focus on the processes they want to apply rather than on the code. The
library is based on gdal to reduce CPU time due to large numpy array imports.

## Basic available operations
- [x] Merging, clipping, re-projecting, padding, resampling, rescaling, windowing
- [x] Raster calculator to design your own operations
- [] Fast raster statistics
- [x] Automatically download and merge SRTM DEM(s) from CGIAR online database

## Install
Pip installation should normally take care of everything for you.

### Using PIP

The easiest way to install PyRasta is using ``pip`` in a terminal
```
$ pip install pyrasta
```

## Examples
#### Build digital elevation model from CGIAR SRTM site
```python
from pyrasta.tools.srtm import from_cgiar_online_database
bounds = (23, 34, 32, 45)
dem = from_cgiar_online_database(bounds)
```

#### Fast clipping of raster by extent or by mask
```python
from pyrasta.raster import Raster
import geopandas
raster_by_extent = Raster("/path/to/your/raster").clip(bounds=(10, 40, 15, 45))
raster_by_mask = Raster("/path/to/your/raster").clip(mask=geopandas.GeoDataFrame.from_file("/path/to/your/layer"))
```