# COMPAS CGAL

CGAL wrapper for the COMPAS framework.

## Installation

```bash
conda create -n compas_cgal python=3.9 compas -c conda-forge
pip install -r requirements.txt
pip install -e .
```

> **Note**: The first time you run `pip install -e .`, it will take longer as C++ libraries are being downloaded. Subsequent compilations will be much faster.

### Examples

Examples files are located in the `scripts` folder.

```bash
python scripts/meshing_remesh.py
```

### Development Setup

Install development dependencies:
```bash
pip install -r requirements-dev.txt
conda install cmake
```

For faster build use the command below. The `--no-build-isolation` flag allows the build process to access dependencies from your local environment, instead of downloading every time them from PyPI. `-v` enables verbose output, and `-e` installs in editable mode for development.
```bash
pip install --no-build-isolation -ve .
```

If you need to rebuild the package:
```bash 
pip install --no-build-isolation -ve . -Ceditable.rebuild=true
```

### Development Guide 

#### How to add a new Module?

Create a new file in the `src` folder with the name of the module you want to add e.g. `new_module.cpp` and `new_module.h`.

- Add the new module to the `CMakeLists.txt` file:

```cmake
nanobind_add_module(
  compas_cgal_ext
  STABLE_ABI
  NB_STATIC
  src/compas_cgal.cpp
  src/meshing.cpp
  src/measure.cpp
  src/new_module.cpp
)
```

- Fill the new module with the necessary code.

```cmake
void init_new_module(nb::module_& m) {
    auto submodule = m.def_submodule("new_module");

    submodule.def(
        "python_function_name",
        &cpp_function_name,
        "description",
        "my_argument1"_a,
        "my_argument2"_a,
    );
}
```

- Add the new module to the `compas_cgal.cpp` file:

```cpp
#include "compas.h"

...
init_new_module(m);
...

NB_MODULE(compas_cgal_ext, m) {
    ...
    init_new_module(m);
}

```

- Build the package:
```bash
pip install --no-build-isolation -ve .
```

- Add the new methods in the __init__.py file:
```python
from .compas_cgal_ext.new_module import python_function_name

__all__ = ["python_function_name"]
```

- Write and example file in scripts folder with profiler.
- Write a test file in tests folder.
- Add documentation.

> **Note**: The types of C++ and Python that much correspond. Instead of following document only, try to read first the [tests](https://github.com/wjakob/nanobind/tree/master/tests) of nanobind.


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
pytest tests/test_nanobind.py
```

Run a specific test function:
```bash
pytest tests/test_nanobind.py::test_add_binding
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
