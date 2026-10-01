# Conda Environment

There are two ways to set up the development environment:

## Using environment.yml (recommended)

``` bash
conda env create -f environment.yml
conda activate cgal-dev
```

## Manual setup

``` bash
conda create -n compas_cgal python=3.9 compas -c conda-forge cmake -y
pip install -r requirements-dev.txt
pip install --no-build-isolation -ve . -Ceditable.rebuild=true
```

Both methods will create and configure the same development environment.
