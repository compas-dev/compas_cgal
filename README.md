# COMPAS CGAL

[![GitHub - License](https://img.shields.io/github/license/compas-dev/compas_cgal.svg)](https://github.com/compas-dev/compas_cgal)
[![Conda - Latest Release](https://anaconda.org/conda-forge/compas_cgal/badges/version.svg)](https://anaconda.org/conda-forge/compas_cgal)

This package provides Python bindings for specific algorithms of CGAL.
The bindings are generated with PyBind11 and data is exchanged using NumPy arrays.

More information is available in the docs:
<https://compas.dev/compas_cgal/>

## Installation

`compas_cgal` is now available via `conda-forge` for Windows, OSX, and Linux,
and can be installed using `conda`.

```bash
conda install COMPAS compas_cgal
```

## Usage

Currently, the following functions are available:

* `boolean_union`
* `boolean_difference`
* `boolean_intersection`
* `intersection_mesh_mesh`
* `remesh`
* `slice_mesh`

These functions can be used directly from `compas_cgal`
or from `compas.geometry` through the plugin mechanism in COMPAS.

For examples, see <https://compas.dev/compas_cgal/examples/>

## Contribute

See [CONTRIBUTING](CONTRIBUTING.md) for more information.

## License

`compas_cgal` is released under the LGPL 3.0 to be compatible with the license of CGAL.
