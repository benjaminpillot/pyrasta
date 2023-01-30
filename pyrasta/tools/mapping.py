# -*- coding: utf-8 -*-

""" Module summary description.

More detailed description.
"""

GDAL_TO_NUMPY = {1: "int8",
                 2: "uint16",
                 3: "int16",
                 4: "uint32",
                 5: "int32",
                 6: "float32",
                 7: "float64",
                 10: "complex64",
                 11: "complex128"}

NUMPY_TO_GDAL = {"int8": 1,
                 "uint16": 2,
                 "int16": 3,
                 "uint32": 4,
                 "int32": 5,
                 "float32": 6,
                 "int64": 7,
                 "float64": 7,
                 "complex64": 10,
                 "complex128": 11}

GDAL_TO_OGR = {1: 0,
               2: 0,
               3: 0,
               4: 0,
               5: 0,
               6: 2,
               7: 2}
