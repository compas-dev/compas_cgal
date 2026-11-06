# Triangulation

`compas_cgal` implements the core COMPAS named structural extension points:

- `compas.geometry.delaunay_triangulation`
- `compas.geometry.constrained_delaunay_triangulation`
- `compas.geometry.conforming_delaunay_triangulation`

The functions accept coordinate buffers directly and return preserved XYZ
coordinates together with a C-contiguous `int32` triangle array. They do not
require a `Tessellation` or other COMPAS geometry object. Conforming Delaunay
triangulation optionally accepts a positive finite `max_edge_length` refinement
target.

::: compas_cgal.triangulation
