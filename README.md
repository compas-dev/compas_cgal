# COMPAS CGAL

CGAL wrapper for the COMPAS framework.

## Installation

```bash
conda create -n compas_cgal python=3.9 compas -c conda-forge
pip install -r requirements.txt
pip install -e .
```

### Examples

Examples files are located in the `scripts` folder.

```bash
python scripts/basic.py
```

### Development Setup

Install development dependencies:
```bash
pip install -r requirements-dev.txt
conda install cmake
```

Compile C++ project in development mode:
```bash
pip install --no-build-isolation -ve .
```

If you need to rebuild the package:
```bash 
pip install --no-build-isolation -ve . -Ceditable.rebuild=true
```


### Development

To speed up C++ development builds when precompiled header is used:

```bash
pip install nanobind scikit-build-core[pyproject]
conda install cmake
pip install --no-build-isolation -ve .
pip install --no-build-isolation -ve . -Ceditable.rebuild=true
```

### Tests

Tests are located in the `tests` folder. 

Run all tests:

```bash
pytest tests/
```

Run with verbose ouput:

```bash
pytest -v tests/
```

Run a specific test file:
```bash
pytest tests/test_basic.py
```

Run a specific test function:
```bash
pytest tests/test_basic.py::test_add_binding
```

### Profiler

For profiling install line_profiler and type the following command.
Differently to Python in-build cProfiler, line_profiler provides time the script takes to run as well as the time of the subfunctions.

```bash
pip install line_profiler
kernprof -l -v -r <path_to_script>
```

## License

BSD License
