from compas.geometry import Polygon, Translation
from compas.datastructures import Mesh
from compas_cgal.triangulation import conforming_delaunay_triangulation
from compas_cgal.triangulation import refined_delaunay_mesh
from compas_view2.app import App

# ==============================================================================
# Constraints
# ==============================================================================

boundary = Polygon.from_sides_and_radius_xy(64, 4)

hole = Polygon.from_sides_and_radius_xy(128, 1)

hole1 = hole.transformed(Translation.from_vector([2, 0, 0]))
hole2 = hole.transformed(Translation.from_vector([-2, 0, 0]))
hole3 = hole.transformed(Translation.from_vector([0, 2, 0]))
hole4 = hole.transformed(Translation.from_vector([0, -2, 0]))

holes = [hole1, hole2, hole3, hole4]

# ==============================================================================
# Triangulation
# ==============================================================================

V, F = conforming_delaunay_triangulation(
    boundary,
    holes=holes,
)

cdt = Mesh.from_vertices_and_faces(V, F)

V, F = refined_delaunay_mesh(
    boundary,
    holes=holes,
    maxlength=0.5,
    is_optimized=True,
)

rdm = Mesh.from_vertices_and_faces(V, F)

# ==============================================================================
# Viz
# ==============================================================================

viewer = App(width=1600, height=900)
viewer.view.camera.position = [0, -1, 13]
viewer.view.camera.look_at([0, 0, 0])

viewer.add(cdt.transformed(Translation.from_vector([-5, 0, 0])))
viewer.add(rdm.transformed(Translation.from_vector([+5, 0, 0])))

viewer.show()
