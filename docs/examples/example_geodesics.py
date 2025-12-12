from pathlib import Path

import numpy as np
from compas.colors import Color
from compas.colors import ColorMap
from compas.datastructures import Mesh
from compas.geometry import Box
from compas.geometry import Point
from compas.geometry import Polyline
from compas.geometry import Translation
from compas_viewer import Viewer
from compas_viewer.config import Config

from compas_cgal.geodesics import HeatGeodesicSolver
from compas_cgal.geodesics import geodesic_isolines
from compas_cgal.geodesics import geodesic_isolines_split
from compas_cgal.geodesics import heat_geodesic_distances


def make_mesh(V, F, offset):
    m = Mesh.from_vertices_and_faces(V, F)
    m.transform(Translation.from_vector([offset[0], offset[1], 0]))
    return m


def make_vertex_colors(distances):
    return {i: cmap(d, minval=distances.min(), maxval=distances.max()) for i, d in enumerate(distances)}


def make_isolines(sources, offset):
    polylines = []
    for pts in geodesic_isolines((V, F), sources, ISOVALUES):
        points = [[pts[i, 0] + offset[0], pts[i, 1] + offset[1], pts[i, 2]] for i in range(len(pts))]
        polylines.append(Polyline(points))
    return polylines


def make_split_meshes(sources, offset):
    meshes = []
    for i, (v, f) in enumerate(geodesic_isolines_split((V, F), sources, SPLIT_ISOVALUES)):
        m = Mesh.from_vertices_and_faces(v.tolist(), f.tolist())
        m.transform(Translation.from_vector([offset[0], offset[1], 0]))
        meshes.append((m, COLORS[i % len(COLORS)]))
    return meshes


def make_source_points(sources, offset):
    return [Point(V[s][0] + offset[0], V[s][1] + offset[1], V[s][2]) for s in sources]


# =============================================================================
# Load mesh
# =============================================================================

FILE = Path(__file__).parent.parent.parent / "data" / "elephant.off"
mesh = Mesh.from_off(FILE)
mesh.quads_to_triangles()
V, F = mesh.to_vertices_and_faces()
V_np = np.array(V)

# =============================================================================
# Config
# =============================================================================

X_OFF, Y_OFF = 0.75, 1.0
ISOVALUES = [i / 50 for i in range(50)]
SPLIT_ISOVALUES = [i / 20 for i in range(20)]
COLORS = [
    Color.red(),
    Color.orange(),
    Color.yellow(),
    Color.green(),
    Color.cyan(),
    Color.blue(),
    Color.purple(),
    Color.magenta(),
]
cmap = ColorMap.from_two_colors(Color.blue(), Color.red())

# =============================================================================
# Single sources
# =============================================================================

src1 = [0]
dist1 = heat_geodesic_distances((V, F), src1)

# =============================================================================
# Multiple sources
# =============================================================================

solver = HeatGeodesicSolver((V, F))
bbox = Box.from_points(V_np)
src2 = list(dict.fromkeys([int(np.argmin(np.linalg.norm(V_np - c, axis=1))) for c in bbox.vertices]))
dist2 = solver.solve(src2)

# =============================================================================
# Viz
# =============================================================================

config = Config()
config.camera.target = [X_OFF, -Y_OFF / 2, 0]
config.camera.position = [X_OFF, -2.0, 0.8]

viewer = Viewer(config=config)

# Row 1: Single Source

g1 = viewer.scene.add_group("Single Source")

g1.add(
    make_mesh(V, F, (0, 0)),
    use_vertexcolors=True,
    vertexcolor=make_vertex_colors(dist1),
    show_lines=False,
)

for pt in make_source_points(src1, (0, 0)):
    g1.add(pt, pointcolor=Color.black(), pointsize=20)

for pl in make_isolines(src1, (X_OFF, 0)):
    g1.add(pl, linecolor=Color.red(), lineswidth=5)

for m, c in make_split_meshes(src1, (2 * X_OFF, 0)):
    g1.add(m, facecolor=c, show_lines=False)

# Row 2: Multiple Sources

g2 = viewer.scene.add_group("Multiple Sources")

g2.add(
    make_mesh(V, F, (0, -Y_OFF)),
    use_vertexcolors=True,
    vertexcolor=make_vertex_colors(dist2),
    show_lines=False,
)

for pt in make_source_points(src2, (0, -Y_OFF)):
    g2.add(pt, pointcolor=Color.black(), pointsize=20)

for pl in make_isolines(src2, (X_OFF, -Y_OFF)):
    g2.add(pl, linecolor=Color.red(), lineswidth=5)

for m, c in make_split_meshes(src2, (2 * X_OFF, -Y_OFF)):
    g2.add(m, facecolor=c, show_lines=False)

viewer.show()
