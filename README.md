# COMPAS CGAL

COMPAS friendly bindings for the CGAL library.

More information is available in the docs:
<https://blockresearchgroup.github.io/compas_cgal/>

## Installation

**compas_cgal requires the very latest of both COMPAS and the COMPAS viewers!**

Note that the CMake-based version of `setup.py` is not working on Windows, yet.
The version using `setuptools` works on Windows and on Mac.

### Mac

```bash
conda create -n cgal python=3.7 python.app eigen boost-cpp gmp mpfr cgal-cpp">=5.0" pybind11 COMPAS">=0.16.0"
conda activate cgal
pip install -e .
```

### Windows

```bash
conda create -n cgal python=3.7 eigen boost-cpp mpir mpfr cgal-cpp">=5.0" pybind11 COMPAS">=0.16.0"
conda activate cgal
pip install -e .
```
