# -*- coding: utf-8 -*-

from distutils.core import setup
from Cython.Build import cythonize

setup(name='BCM', ext_modules=cythonize(["cm.py", ]), )
