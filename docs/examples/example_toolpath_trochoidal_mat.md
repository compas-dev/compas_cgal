# MAT-Based Trochoidal Toolpath

This example demonstrates adaptive trochoidal pocket toolpath generation from a 2D polygon using medial axis transform (MAT) samples derived from the straight skeleton, returned as circular and linear motion primitives.

Key Features:

* Medial-axis edge centerlines for cutter-center motion
* Circular (`arc`) and linear (`line`) primitives suitable for G-code/robot paths
* Direct rendering of `Line`/`Arc` geometry in `compas_viewer`
* Lead-in, lead-out, and inter-path link operations (`cut`/`lead_in`/`lead_out`/`link`)
* Optional Z-safe transitions with `retract`/`plunge` between paths (`cut_z`, `clearance_z`)
* Direct COMPAS geometry output (`Line`/`Arc`/`Circle`) via `*_compas` wrappers
* Radius maximization from centerline toward pocket boundary

```python
---8<--- "docs/examples/example_toolpath_trochoidal_mat.py"
```
