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

## Usage

The provided functionality can be used directly from the `compas_cgal` package
or from `compas.geometry` through the plugin mechanism in COMPAS.

For examples, see <https://compas.dev/compas_cgal/latest/examples.html>.

## Contribute

See [CONTRIBUTING](CONTRIBUTING.md) for more information.

## License

`compas_cgal` is released under the LGPL 3.0 to be compatible with the license of CGAL.
