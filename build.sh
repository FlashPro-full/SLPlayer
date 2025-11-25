#!/bin/bash

echo "Building SLPlayer executable..."
echo ""

# Check if PyInstaller is installed
if ! python -c "import PyInstaller" 2>/dev/null; then
    echo "PyInstaller is not installed. Installing..."
    pip install pyinstaller
fi

echo ""
echo "Cleaning previous builds..."
rm -rf build dist

echo ""
echo "Building executable..."
pyinstaller --clean build_exe.spec

if [ $? -eq 0 ]; then
    echo ""
    echo "Build completed successfully!"
    echo "Executable is in the 'dist' folder."
else
    echo ""
    echo "Build failed!"
    exit 1
fi


