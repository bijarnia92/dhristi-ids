#!/bin/bash

echo "===================================="
echo "  IDS Project Setup for Linux/macOS"
echo "===================================="

echo "Step 1: Checking Python installation..."
python3 --version
if [ $? -ne 0 ]; then
    echo "ERROR: Python3 not found! Please install Python3"
    exit 1
fi

echo ""
echo "Step 2: Installing required libraries..."
pip3 install scapy scikit-learn numpy python-dateutil

echo ""
echo "Step 3: Testing installation..."
python3 -c "import scapy; import sklearn; print('SUCCESS: All libraries installed!')"

echo ""
echo "Step 4: Running test mode..."
python3 network_ids.py test

echo ""
echo "===================================="
echo "Setup Complete! Your IDS is ready."
echo "===================================="
