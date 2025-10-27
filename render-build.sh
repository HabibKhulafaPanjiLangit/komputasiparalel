# Render.com build script
#!/bin/bash

# Install MPI
apt-get update
apt-get install -y mpich libmpich-dev gcc g++

# Install Python packages
pip install -r requirements.txt
