# COMPAS CGAL

COMPAS friedly bindings for the CGAL library.

## Installation

**This has only been tested on Mac.**

```bash
conda create -n cgal python=3.7 python.app eigen boost-cpp cgal-cpp">=5.0" pybind11 COMPAS --yes
conda activate cgal
pip install -e .
```

```bash
python ./scripts/test_hello.py
Hello COMPAS
```

```bash
```
