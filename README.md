# PyRasta

[![Maintenance](https://img.shields.io/badge/Maintained%3F-yes-green.svg)](https://framagit.org/benjaminpillot/pyraster/graphs/commit-activity)

Some tools for fast and easy raster processing, based on gdal (numpy usage is reduced to the minimum).

## Introduction
PyRasta is a small Python library which aims at interfacing gdal functions and methods in an easy 
way, so that users may only focus on the processes they want to apply rather than on the code. The
library is based on gdal to reduce CPU time due to large numpy array imports.

## Basic available operations
- [x] Merging, clipping, re-projecting, padding, resampling, rescaling, windowing
- [x] Raster calculator to design your own operations
- [x] Automatically download and merge SRTM DEM(s) from CGIAR online database

## Install
Pip installation should normally take care of everything for you.

### Using PIP

The easiest way to install PyRasta is using ``pip`` in a terminal
```
$ pip install pyrasta
```
