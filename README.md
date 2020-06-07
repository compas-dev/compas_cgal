# COMPAS CGAL

COMPAS friedly bindings for the CGAL library.

## Installation

**Update COMPAS to 0.16.0 and the viewers to the latest version!**

Note that the CMake-based version of `setup.py` is not working on Windows, yet.
The version using `setuptools` works on Windows and on Mac.

### Mac

```bash
conda create -n cgal python=3.7 python.app eigen boost-cpp gmp mpfr cgal-cpp">=5.0" pybind11 PySide2 PyOpenGL COMPAS=0.16.0
conda activate cgal
pip install git+https://github.com/compas-dev/compas_viewers.git#egg=compas_viewers
pip install -e .
```

### Windows

```bash
conda create -n cgal python=3.7 eigen boost-cpp mpir mpfr cgal-cpp">=5.0" pybind11 PySide2 COMPAS=0.16.0
conda activate cgal
pip install wheels/PyOpenGL‑3.1.5‑cp37‑cp37m‑win_amd64.whl
pip install git+https://github.com/compas-dev/compas_viewers.git#egg=compas_viewers
pip install -e .
```

## Examples

### 1. Booleans

**Mesh-Mesh Union.**

![images/cgal_boolean_union.png](images/cgal_boolean_union.png)

**Mesh-Mesh Difference.**

![images/cgal_boolean_difference.png](images/cgal_boolean_difference.png)
![images/cgal_boolean_difference_remeshed.png](images/cgal_boolean_difference_remeshed.png)

**Mesh-Mesh Intersection.**

![images/cgal_boolean_intersection.png](images/cgal_boolean_intersection.png)

*To do:*

* Add options:
  * remesh solution (on C++ side)
  * dihedral angle for feature preservation
  * number of remeshing iterations
  * target edge length for remeshing
* Preserve intersection edges during remeshing
* Remesh protected edges to target length
* Combine boolean operations (on C++ side)

### 2. Slicing

**Slice mesh by plane.**

![images/cgal_slicer.png](images/cgal_slicer.png)

*To do:*

* Simplify slice polylines
* Slice by multiple planes (on C++ side)
* Return more than one polygon (fix bug)

### 3. Meshing

**Mesh remeshing.**

![images/cgal_remesh.png](images/cgal_remesh.png)

*To do:*

* Fair
* Refine
* Triangulate

### 4. Mesh-Mesh Intersections

### 5. Connected Components

### 6. Collisions

*To Do:*

* Intersecting meshes
