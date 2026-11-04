"""Static consumer coverage for public CGAL coordinate and index inputs."""

import numpy as np
from compas._typing import TriangleMeshInput
from compas.geometry import ConstrainedDelaunay
from compas.geometry import Delaunay
from compas.geometry import Tessellation

from compas_cgal.booleans import boolean_difference_mesh_mesh
from compas_cgal.booleans import boolean_intersection_mesh_mesh
from compas_cgal.booleans import boolean_union_mesh_mesh
from compas_cgal.plugins.booleans import _boolean_difference_mesh_mesh
from compas_cgal.plugins.booleans import _boolean_intersection_mesh_mesh
from compas_cgal.plugins.booleans import _boolean_union_mesh_mesh
from compas_cgal.plugins.triangulation import _triangulate_planar_domain
from compas_cgal.plugins.triangulation import _triangulate_planar_points
from compas_cgal.plugins.trimesh import trimesh_slice
from compas_cgal.types import Faces
from compas_cgal.types import Vertices
from compas_cgal.types import VerticesFaces


def consume_vertices(value: Vertices) -> None:
    pass


def consume_faces(value: Faces) -> None:
    pass


def consume_mesh(value: VerticesFaces) -> None:
    pass


vertices_list = [[0.0, 0.0, 0.0], [1.0, 0.0, 0.0], [0.0, 1.0, 0.0]]
vertices_tuple = ((0.0, 0.0, 0.0), (1.0, 0.0, 0.0), (0.0, 1.0, 0.0))
vertices_float32 = np.asarray(vertices_list, dtype=np.float32)
vertices_float64 = np.asarray(vertices_list, dtype=np.float64)
vertices_int32 = np.asarray(vertices_list, dtype=np.int32)
vertices_int64 = np.asarray(vertices_list, dtype=np.int64)
vertices_fortran = np.asfortranarray(vertices_float64)
vertices_sliced = np.pad(vertices_float64, ((0, 0), (0, 1)))[:, :3]
vertices_readonly = vertices_float64.copy()
vertices_readonly.flags.writeable = False

faces_list = [[0, 1, 2]]
faces_tuple = ((0, 1, 2),)
faces_int32 = np.asarray(faces_list, dtype=np.int32)
faces_int64 = np.asarray(faces_list, dtype=np.int64)
faces_fortran = np.asfortranarray(faces_int32)
faces_sliced = np.pad(faces_int32, ((0, 0), (0, 1)))[:, :3]
faces_readonly = faces_int32.copy()
faces_readonly.flags.writeable = False

consume_vertices(vertices_list)
consume_vertices(vertices_tuple)
consume_vertices(vertices_float32)
consume_vertices(vertices_float64)
consume_vertices(vertices_fortran)
consume_vertices(vertices_sliced)
consume_vertices(vertices_readonly)

consume_faces(faces_list)
consume_faces(faces_tuple)
consume_faces(faces_int32)
consume_faces(faces_int64)
consume_faces(faces_fortran)
consume_faces(faces_sliced)
consume_faces(faces_readonly)

consume_mesh((vertices_list, faces_list))
consume_mesh((vertices_tuple, faces_tuple))
consume_mesh((vertices_float32, faces_int64))
consume_mesh((vertices_fortran, faces_sliced))
consume_mesh((vertices_readonly, faces_readonly))

triangle_mesh: TriangleMeshInput = (vertices_float32, faces_int64)
boolean_union_mesh_mesh(triangle_mesh, (vertices_fortran, faces_sliced))
boolean_difference_mesh_mesh(triangle_mesh, (vertices_readonly, faces_readonly))
boolean_intersection_mesh_mesh(triangle_mesh, (vertices_list, faces_list))
_boolean_union_mesh_mesh(triangle_mesh, triangle_mesh)
_boolean_difference_mesh_mesh(triangle_mesh, triangle_mesh)
_boolean_intersection_mesh_mesh(triangle_mesh, triangle_mesh)

tessellation = Tessellation(vertices_float64, faces_int32)
trimesh_slice(tessellation, [([0.0, 0.0, 0.0], [0.0, 0.0, 1.0])])

domain_float32 = np.asarray(
    [[0.0, 0.0, 0.0], [3.0, 0.0, 0.0], [3.0, 3.0, 0.0], [0.0, 3.0, 0.0]],
    dtype=np.float32,
)
hole_float64 = np.asarray(
    [[[1.0, 1.0, 0.0], [2.0, 1.0, 0.0], [2.0, 2.0, 0.0], [1.0, 2.0, 0.0]]],
    dtype=np.float64,
)
_triangulate_planar_points(vertices_float32, strategy=Delaunay())
_triangulate_planar_points(vertices_float64, strategy=Delaunay())
_triangulate_planar_points(vertices_int32, strategy=Delaunay())
_triangulate_planar_points(vertices_int64, strategy=Delaunay())
_triangulate_planar_domain(
    domain_float32,
    holes=hole_float64,
    constraints=np.empty((0, 0, 3), dtype=np.float32),
    points=np.empty((0, 3), dtype=np.float64),
    strategy=ConstrainedDelaunay(),
)
