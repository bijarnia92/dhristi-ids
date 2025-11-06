@echo off
echo ====================================
echo  IDS Project Setup for Windows
echo ====================================

echo Step 1: Checking Python installation...
python --version
if %errorlevel% neq 0 (
    echo ERROR: Python not found! Please install Python from https://python.org/downloads/
    pause
    exit
)

echo.
echo Step 2: Installing required libraries...
pip install scapy scikit-learn numpy python-dateutil

echo.
echo Step 3: Testing installation...
python -c "import scapy; import sklearn; print('SUCCESS: All libraries installed!')"

echo.
echo Step 4: Running test mode...
python network_ids.py test

echo.
echo ====================================
echo Setup Complete! Your IDS is ready.
echo ====================================
pause
