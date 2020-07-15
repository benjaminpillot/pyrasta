# -*- coding: utf-8 -*-

""" Module summary description.

More detailed description.
"""
import os
from tempfile import mkstemp


class File:

    def __init__(self, path):
        self.path = path

    def __enter__(self):
        return self.path


class TempFile(File):

    def __del__(self):
        try:
            os.remove(self.path)
        except FileNotFoundError:
            pass


class MemmapFile(TempFile):

    def __init__(self):
        super().__init__(mkstemp(suffix='.dat')[1])

    def __exit__(self, exc_type, exc_val, exc_tb):
        del self


class RasterTempFile(TempFile):
    """ Create temporary raster file

    """
    def __init__(self):
        super().__init__(mkstemp(suffix='.tif')[1])
