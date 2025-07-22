#!/bin/bash

# Author: Qing Yao
# Email: qy2290@columbia.edu
# To create virtual environment for analysis 

# Set environment name
ENV_NAME="geo_env"

echo "Creating Conda environment: $ENV_NAME"
conda create --name $ENV_NAME python=3.11 -y

echo "Activating Conda environment"
source activate $ENV_NAME

echo "Installing essential packages"
conda install -y -c conda-forge pandas numpy scipy h5py geopandas geopy matplotlib python-dateutil textwrap3 jupyterlab ipykernel

### to avoid potential conflicts among packages, using conda forge to install first and then pip to install the rest

# echo "Installing additional dependencies"
# pip install python-dateutil textwrap3

### if you are using juypter notebook, you can install the following packages

echo "Adding Conda environment to Jupyter"
python -m ipykernel install --user --name=$ENV_NAME --display-name "Python ($ENV_NAME)"

echo "Setup complete. To activate, run: conda activate $ENV_NAME"
