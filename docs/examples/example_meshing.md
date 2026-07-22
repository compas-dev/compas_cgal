# Mesh Remeshing

![Mesh Remeshing](../assets/images/example_meshing.png)

This example demonstrates `trimesh_remesh` and its `protect_boundary` option using COMPAS CGAL.

A dense 7-lobe star disk (triangulated with `refined_delaunay_mesh`) is remeshed to a coarse target edge length two ways:

* **Left — `protect_boundary=False`**: boundary edges are re-sampled to the target, so the finely sampled star rim collapses to a coarse, faceted polygon (~37 perimeter vertices).
* **Right — `protect_boundary=True`**: boundary edges are constrained, so the perimeter density is maintained — the rim stays a smooth, finely sampled star (~330 perimeter vertices) while the interior is coarsened.

Both meshes are false-colored by local vertex density (blue = coarse, red = dense) on a shared scale, so the maintained perimeter reads as a hot band on the right.

Use `protect_boundary` when an open mesh's border curve must survive remeshing verbatim. The companion parameter `protect_sharp_edges_angle_deg` similarly constrains interior feature edges whose dihedral angle exceeds a threshold.

Key Features:

* Remeshing with a target edge length via `trimesh_remesh`
* Preserving perimeter sampling with `protect_boundary`
* Generating the input star with `refined_delaunay_mesh`
* Side-by-side visualization of the two results

```python
---8<--- "docs/examples/example_meshing.py"
```
