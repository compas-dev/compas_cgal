from compas.geometry import ConformingDelaunay
from compas.geometry import ConstrainedDelaunay
from compas.geometry import Polygon
from compas.geometry import Translation
from compas.geometry import TriangulationQuality
from compas.geometry import triangulate_planar_domain
from compas_viewer import Viewer

boundary = Polygon.from_sides_and_radius_xy(64, 4)

hole = Polygon.from_sides_and_radius_xy(128, 1)

hole1 = hole.transformed(Translation.from_vector([2, 0, 0]))
hole2 = hole.transformed(Translation.from_vector([-2, 0, 0]))
hole3 = hole.transformed(Translation.from_vector([0, 2, 0]))
hole4 = hole.transformed(Translation.from_vector([0, -2, 0]))

holes = [hole1, hole2, hole3, hole4]

cdt = triangulate_planar_domain(
    boundary,
    holes=holes,
    strategy=ConstrainedDelaunay(),
)
cdt = cdt.to_mesh()

rdm = triangulate_planar_domain(
    boundary,
    holes=holes,
    strategy=ConformingDelaunay(TriangulationQuality(max_edge_length=0.5)),
)
rdm = rdm.to_mesh()

# ==============================================================================
# Visualize
# ==============================================================================

viewer = Viewer()

viewer.renderer.camera.target = [0, 0, 0]
viewer.renderer.camera.position = [0, -1, 13]

viewer.scene.add(cdt.transformed(Translation.from_vector([-5, 0, 0])))
viewer.scene.add(rdm.transformed(Translation.from_vector([+5, 0, 0])))

viewer.show()
