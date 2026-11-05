# Mesh Remeshing

![Mesh Remeshing](../assets/images/example_meshing.png)

This example triangulates a RhinoVault mesh and remeshes its raw vertex and triangle buffers to a uniform target edge length with COMPAS CGAL.

Key Features:

* Loading PLY mesh files
* Remeshing with a target edge length via `trimesh_remesh`
* Using structural vertex and triangle buffers at the numerical boundary
* Constructing a mesh explicitly for visualization

```python
---8 < ---"docs/examples/example_meshing.py"
```
