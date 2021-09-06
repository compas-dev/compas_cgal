# COMPAS CGAL

![build](https://github.com/compas-dev/compas_cgal/workflows/build/badge.svg)
[![GitHub - License](https://img.shields.io/github/license/compas-dev/compas_cgal.svg)](https://github.com/compas-dev/compas_cgal)
[![Conda - Latest Release](https://anaconda.org/conda-forge/compas_cgal/badges/version.svg)](https://anaconda.org/conda-forge/compas_cgal)
[![Conda - Platform](https://img.shields.io/conda/pn/conda-forge/compas_cgal)](https://anaconda.org/conda-forge/compas_cgal)

This package provides Python bindings for specific algorithms of CGAL.
The bindings are generated with PyBind11 and data is exchanged using NumPy arrays.

More information is available in the docs:
<https://compas.dev/compas_cgal/>

## Installation

`compas_cgal` is available via `conda-forge` for Windows, OSX, and Linux,
and can be installed using `conda`.

```bash
conda create -n cgal -c conda-forge compas compas_cgal --yes
```

## Dev Install

Create a development environment with the required dependencies using `conda`
and compile and install an editable version of `compas_cgal` using `setuptools`.

**Windows**:

```bash
conda create -n cgal-dev python=3.8 mpir mpfr boost-cpp eigen=3.3 cgal-cpp=5.2 pybind11 compas compas_view2 --yes
conda activate cgal-dev
git clone https://github.com/compas-dev/compas_cgal
cd compas_cgal
pip install -e .
```

**Mac**:

```bash
conda create -n cgal-dev python=3.8 gmp mpfr boost-cpp eigen=3.3 cgal-cpp=5.2 pybind11 compas compas_view2 --yes
conda activate cgal-dev
git clone https://github.com/compas-dev/compas_cgal
cd compas_cgal
pip install -e .
```

> Note that the version of eigen is important and should be `3.3`.

To add a new c++ module to the Python wrapper, or to exclude some of the existing modules during development
you can modify the list of extension modules in `setup.py`.

```python
ext_modules = [
    Extension(
        'compas_cgal._cgal',
        sorted([
            'src/compas_cgal.cpp',
            'src/compas.cpp',
            'src/meshing.cpp',
            'src/booleans.cpp',
            'src/slicer.cpp',
            'src/intersections.cpp',
            'src/measure.cpp',
        ]),
        include_dirs=[
            './include',
            get_eigen_include(),
            get_pybind_include()
        ],
        library_dirs=[
            get_library_dirs(),
        ],
        libraries=['mpfr', 'gmp'],
        language='c++'
    ),
]
```

## Usage

The provided functionality can be used directly from the `compas_cgal` package
or from `compas.geometry` through the plugin mechanism in COMPAS.

For examples, see <https://compas.dev/compas_cgal/latest/examples.html>.

## License

`compas_cgal` is released under the LGPL 3.0 to be compatible with the license of CGAL.
