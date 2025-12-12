# Geodesic Distances and Isolines

![Geodesics](../assets/images/example_geodesics.png)

This example demonstrates geodesic distance computation, isoline extraction, and mesh splitting using COMPAS CGAL.

The visualization shows two rows:

* **Row 1 (Single Source)**: Geodesic distances from a single vertex
* **Row 2 (Multiple Sources)**: Geodesic distances from all bounding box corners

Each row displays three columns:

* **Heat Field**: Mesh colored by geodesic distance (blue → red gradient) with source points marked in black
* **Isolines**: Extracted isoline polylines at regular distance intervals
* **Split Mesh**: Mesh split into components along the isolines, each colored differently

Key Features:

* Heat method geodesic distance computation via ``heat_geodesic_distances``
* Reusable solver via ``HeatGeodesicSolver`` for multiple queries
* Isoline extraction as polylines via ``geodesic_isolines``
* Mesh splitting along isolines via ``geodesic_isolines_split``

```python
---8<--- "docs/examples/example_geodesics.py"
```
