#!/usr/bin/env python
# encoding: utf-8
"""
setup.py

Created by Pierre-Julien Grizel et al.
Copyright (c) 2016 NumeriCube. All rights reserved.

Basic package initialization
Good read on this: https://blog.ionelmc.ro/2014/05/25/python-packaging/#the-structure
"""
from __future__ import unicode_literals

__author__ = ""
__copyright__ = "Copyright 2016, NumeriCube"
__credits__ = ["Pierre-Julien Grizel"]
__license__ = "CLOSED SOURCE"
__version__ = "TBD"
__maintainer__ = "Pierre-Julien Grizel"
__email__ = "pjgrizel@numericube.com"
__status__ = "Production"

from glob import glob
import sys
import os
from os.path import basename
from os.path import splitext

import setuptools

if sys.version_info < (3, 5):
    sys.exit("Sorry, Python < 3.5 is not supported")

# with open("README.md", "r") as fh:
# long_description = fh.read()
long_description = ""

# Can't do this because setuptools doesn't support https stuff
# with open('requirements.txt') as f:
#     requirements = f.read().splitlines()

setuptools.setup(
    name="ecoclassifier",
    version=os.environ.get("TRAVIS_TAG", "development-version"),
    author="Pierre-Julien Grizel",
    author_email="pjgrizel@numericube.com",
    description="Majurca's eco-classifier program",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/numericube/majurca-ecoclassifier",
    packages=setuptools.find_packages("src"),
    package_dir={"": "src"},
    py_modules=[splitext(basename(path))[0] for path in glob("src/*.py")],
    include_package_data=True,
    # install_requires=requirements,
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    entry_points={"console_scripts": ["dmake=dmake.dmake:make"]},
)
