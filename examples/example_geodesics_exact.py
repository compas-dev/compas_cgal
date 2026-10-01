from pathlib import Path

from compas.colors import Color
from compas.colors import ColorMap
from compas.datastructures import Mesh
from compas.geometry import Polyline
from compas_viewer import Viewer
from compas_viewer.config import Config

from compas_cgal.geodesics import exact_geodesic_distances_from_points
from compas_cgal.isolines import isolines

mesh = Mesh.from_off(Path(__file__).parent.parent.parent / "data" / "elephant.off")
mesh.quads_to_triangles()

source = mesh.face_centroid(0)
distances = exact_geodesic_distances_from_points(mesh, [source])
polylines = isolines(mesh, distances, n=10, resample=False)

cmap = ColorMap.from_two_colors(Color.blue(), Color.red())
colors = {vertex: cmap(d, minval=distances.min(), maxval=distances.max()) for vertex, d in zip(mesh.vertices(), distances)}

config = Config()
config.camera.position = [0.0, -1.25, 0.6]
config.camera.target = [0.0, 0.0, 0.0]
config.renderer.show_grid = False
viewer = Viewer(config=config)
viewer.scene.add(mesh, use_vertexcolors=True, vertexcolor=colors, show_lines=False)
viewer.scene.add(source, pointcolor=Color.black(), pointsize=20)
for polyline in polylines:
    viewer.scene.add(Polyline(polyline), linecolor=Color.black(), lineswidth=5)
viewer.show()
