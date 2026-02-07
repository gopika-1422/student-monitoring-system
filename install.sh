#!/bin/bash

echo "================================================"
echo "Student Monitoring System - Installation"
echo "================================================"
echo ""

# Check Python
echo "Checking Python installation..."
if ! command -v python3 &> /dev/null; then
    echo "ERROR: Python 3 is not installed"
    echo "Please install Python 3.8+ first"
    exit 1
fi

python3 --version

echo ""
echo "Installing required packages..."
echo "This may take several minutes..."
echo ""

# Detect OS
if [[ "$OSTYPE" == "darwin"* ]]; then
    echo "Detected macOS"
    
    # Check for Homebrew
    if ! command -v brew &> /dev/null; then
        echo "Installing Homebrew..."
        /bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
    fi
    
    echo "Installing cmake..."
    brew install cmake
    
elif [[ "$OSTYPE" == "linux-gnu"* ]]; then
    echo "Detected Linux"
    
    echo "Installing system dependencies..."
    sudo apt-get update
    sudo apt-get install -y python3-pip cmake build-essential libopencv-dev python3-opencv
fi

echo ""
echo "Installing Python packages..."

pip3 install --upgrade pip

echo "Installing opencv-python..."
pip3 install opencv-python

echo "Installing numpy..."
pip3 install numpy

echo "Installing Pillow..."
pip3 install Pillow

echo "Installing cmake..."
pip3 install cmake

echo "Installing dlib (this may take a while)..."
pip3 install dlib

echo "Installing face-recognition..."
pip3 install face-recognition

echo "Installing tabulate..."
pip3 install tabulate

echo ""
echo "================================================"
echo "Installation Complete!"
echo "================================================"
echo ""
echo "To run the application:"
echo "  python3 student_monitor_app.py"
echo ""
echo "To test your camera:"
echo "  python3 test_camera.py"
echo ""
echo "To manage database:"
echo "  python3 db_manager.py"
echo ""
