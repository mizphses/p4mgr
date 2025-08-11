#!/usr/bin/env python
from distutils.core import setup
from distutils.extension import Extension
from Cython.Build import cythonize
import os

# Path to the rpi-rgb-led-matrix library
rgb_lib_path = os.path.abspath("../../rpi-rgb-led-matrix")

extensions = [
    Extension(
        "core",
        ["core.pyx"],
        include_dirs=[os.path.join(rgb_lib_path, "include")],
        libraries=["rgbmatrix"],
        library_dirs=[os.path.join(rgb_lib_path, "lib")],
        language="c++",
        extra_compile_args=["-O3", "-Wall"],
        extra_link_args=["-Wl,-rpath," + os.path.join(rgb_lib_path, "lib")]
    ),
    Extension(
        "graphics",
        ["graphics.pyx"],
        include_dirs=[os.path.join(rgb_lib_path, "include")],
        libraries=["rgbmatrix"],
        library_dirs=[os.path.join(rgb_lib_path, "lib")],
        language="c++",
        extra_compile_args=["-O3", "-Wall"],
        extra_link_args=["-Wl,-rpath," + os.path.join(rgb_lib_path, "lib")]
    )
]

setup(
    name="rgbmatrix",
    ext_modules=cythonize(extensions)
)