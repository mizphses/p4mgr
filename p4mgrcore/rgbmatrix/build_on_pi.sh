#!/bin/bash
# Build script for Raspberry Pi
# Run this script on your Raspberry Pi to compile the Cython extensions

set -e

echo "Building RGBMatrix Python extensions on Raspberry Pi..."

# Check if we're on a Raspberry Pi
if [ ! -f /proc/device-tree/model ] || ! grep -q "Raspberry Pi" /proc/device-tree/model; then
    echo "Warning: This doesn't appear to be a Raspberry Pi"
fi

# Path to rpi-rgb-led-matrix library
RGB_LIB_PATH="../../rpi-rgb-led-matrix"

# Check if the library exists
if [ ! -d "$RGB_LIB_PATH" ]; then
    echo "Error: rpi-rgb-led-matrix library not found at $RGB_LIB_PATH"
    exit 1
fi

# Build the C++ library first
echo "Building rpi-rgb-led-matrix library..."
(cd "$RGB_LIB_PATH" && make)

# Install required Python packages
echo "Installing Python dependencies..."
pip3 install cython

# Generate C++ files from Cython
echo "Generating C++ files from Cython..."
cython3 --cplus -o core.cpp core.pyx
cython3 --cplus -o graphics.cpp graphics.pyx

# Compile the Python extension
echo "Compiling Python extension..."
python3 -m pip install --upgrade pip setuptools wheel
python3 setup.py build_ext --inplace

echo "Build complete! The .so files should now be available."
echo "You can test the installation with: python3 -c 'from p4mgrcore.rgbmatrix import RGBMatrix'"