# -*- coding: utf-8 -*-

""" Module summary description.

More detailed description.
"""
import os
import uuid
from tempfile import mkstemp, gettempdir


def _copy_to_file(raster, out_file):
    """

    """
    try:
        raster._gdal_driver.CopyFiles(out_file, raster._file)
        # out_ds = raster._gdal_driver.CreateCopy(out_file, raster._gdal_dataset, strict=0)
        # out_ds = None
        return 0
    except RuntimeError:
        return 1


class File:

    def __init__(self, path):
        self.path = path

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        pass


class TempFile(File):

    def __del__(self):
        try:
            os.remove(self.path)
        except FileNotFoundError:
            pass


class NamedTempFile(TempFile):

    def __init__(self, extension):
        self.name = os.path.join(gettempdir(), str(uuid.uuid4()))
        super().__init__(self.name + "." + extension)


class ShapeTempFile(NamedTempFile):

    def __init__(self):
        super().__init__("shp")

    def __del__(self):
        super().__del__()
        for ext in [".shx", ".dbf", ".prj", ".cpg"]:
            try:
                os.remove(self.name + ext)
            except FileNotFoundError:
                pass


class RasterTempFile(TempFile):
    """ Create temporary raster file

    """
    def __init__(self, extension):
        super().__init__(mkstemp(suffix='.' + extension)[1])


class VrtTempFile(TempFile):

    def __init__(self):
        super().__init__(mkstemp(suffix='.vrt')[1])
