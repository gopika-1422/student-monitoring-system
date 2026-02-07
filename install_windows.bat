@echo off
echo ================================================
echo Student Monitoring System - Installation
echo ================================================
echo.

echo Checking Python installation...
python --version
if errorlevel 1 (
    echo ERROR: Python is not installed or not in PATH
    echo Please install Python 3.8+ from https://www.python.org/
    pause
    exit /b 1
)

echo.
echo Installing required packages...
echo This may take several minutes...
echo.

echo Installing OpenCV...
pip install opencv-python

echo Installing NumPy...
pip install numpy

echo Installing Pillow...
pip install Pillow

echo Installing CMake...
pip install cmake

echo Installing dlib (this may take a while)...
pip install dlib

echo Installing face-recognition...
pip install face-recognition

echo Installing tabulate for database manager...
pip install tabulate

echo.
echo ================================================
echo Installation Complete!
echo ================================================
echo.
echo To run the application:
echo   python student_monitor_app.py
echo.
echo To test your camera:
echo   python test_camera.py
echo.
echo To manage database:
echo   python db_manager.py
echo.
pause
