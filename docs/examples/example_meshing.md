# Mesh Remeshing

![Mesh Remeshing](../assets/images/example_meshing.png)

This example demonstrates how to remesh a triangle mesh with COMPAS CGAL, and how the `protect_boundary` option changes the result on an open mesh.

A RhinoVault funicular shell is triangulated and remeshed to the same coarse target edge length two ways, shown side by side (each drawn over the faint original for reference):

* **Left — `protect_boundary=False`** (default): boundary edges are re-sampled to the target length, so the shell's open perimeter is coarsened and its corners rounded.
* **Right — `protect_boundary=True`**: every boundary edge is constrained, so the supported perimeter is preserved verbatim while the interior is coarsened.

The companion parameter `protect_sharp_edges_angle_deg` similarly constrains interior feature edges whose dihedral angle exceeds a threshold.

Key Features:

* Loading PLY mesh files
* Remeshing with a target edge length via `trimesh_remesh`
* Preserving an open boundary with `protect_boundary`
* Side-by-side visualization of the two results over the original

```python
---8<--- "docs/examples/example_meshing.py"
```
