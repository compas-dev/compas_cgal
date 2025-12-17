from pathlib import Path

import numpy as np
from compas.colors import Color
from compas.datastructures import Mesh
from compas.geometry import Polyline
from compas_viewer import Viewer

from compas_cgal.geodesics import heat_geodesic_distances
from compas_cgal.isolines import isolines
from compas_cgal.subdivision import mesh_subdivide_loop

# =============================================================================
# Load mesh and subdivide
# =============================================================================

FILE = Path(__file__).parent.parent.parent / "data" / "elephant.off"
mesh = Mesh.from_off(FILE)
mesh.quads_to_triangles()

V, F = mesh_subdivide_loop(mesh.to_vertices_and_faces(), k=2) # k=4 for proper smoothness
mesh = Mesh.from_vertices_and_faces(V.tolist(), F.tolist())

# =============================================================================
# Find source vertices: 4 feet and snout
# =============================================================================

V = np.array(mesh.vertices_attributes("xyz"))

# feet: find lowest Y vertex in each XZ quadrant
y_min = V[:, 1].min()
low_verts = np.where(V[:, 1] < y_min + 0.15)[0]

feet = []
for sx in [-1, 1]:  # back/front (X)
    for sz in [-1, 1]:  # left/right (Z)
        mask = (np.sign(V[low_verts, 0]) == sx) & (np.sign(V[low_verts, 2]) == sz)
        candidates = low_verts[mask]
        if len(candidates):
            foot = candidates[np.argmin(V[candidates, 1])]
            feet.append(int(foot))

# snout: max X (trunk tip)
snout = int(np.argmax(V[:, 0]))

sources = feet + [snout]

# =============================================================================
# Compute scalar field and extract isolines
# =============================================================================

vf = mesh.to_vertices_and_faces()
distances = heat_geodesic_distances(vf, sources)

for key, d in zip(mesh.vertices(), distances):
    mesh.vertex_attribute(key, "distance", d)

polylines = isolines(mesh, "distance", n=300, smoothing=0, resample=False)

# =============================================================================
# Viz
# =============================================================================

viewer = Viewer()

viewer.scene.add(mesh, show_lines=False)

for pts in polylines:
    points = [pts[i].tolist() for i in range(len(pts))]
    viewer.scene.add(Polyline(points), linecolor=Color.red(), lineswidth=3)

viewer.show()
