from setuptools import setup, find_packages

import pyraster

with open("README.md", 'r') as fh:
    long_description = fh.read()

with open("requirements.txt") as req:
    install_req = req.read().splitlines()

setup(name='pyraster',
      version=pyraster.__version__,
      description='Some tools for fast and easy raster processing',
      long_description=long_description,
      long_description_content_type="text/markdown",
      url='https://framagit.org/benjaminpillot/pyraster',
      author='Benjamin Pillot',
      author_email='benjaminpillot@riseup.net',
      install_requires=install_req,
      python_requires='>=3',
      license='MIT',
      packages=find_packages(),
      zip_safe=False)