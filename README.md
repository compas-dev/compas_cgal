# COMPAS CGAL

COMPAS friedly bindings for the CGAL library.

## Installation

**This has only been tested on Mac.**

```bash
conda create -n cgal python=3.7 python.app eigen boost-cpp gmp mpfr cgal-cpp">=5.0" pybind11
conda activate cgal
conda install COMPAS
conda install PySide2 PyOpenGL
pip install git+https://github.com/compas-dev/compas_viewers.git#egg=compas_viewers
pip install -e .
```

## Repo Structure

The `ext_modules` paert of `setup.py` shows where the important bits are.

```python
# setup.py

ext_modules = [
    Extension(
        'compas_cgal._cgal',
        sorted([
            'src/hello.cpp',
            'src/mesh.cpp',
            'src/meshing.cpp',
            'src/booleans.cpp',
            'src/compas_cgal.cpp',
        ]),
        include_dirs=[
            './include',
            get_eigen_include(),
            get_pybind_include()
        ],
        library_dirs=None,
        libraries=['mpfr', 'gmp'],
        language='c++'
    ),
]
```

## Examples

### 1. Hello

```bash
python ./scripts/test_hello.py
```

```bash
Hello COMPAS
```

### 2. Booleans

```bash
python ./scripts/test_booleans.py
```

![images/cgal_boolean_union.png](images/cgal_boolean_union.png)
