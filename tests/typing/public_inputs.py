"""Static consumer coverage for public CGAL coordinate and index inputs."""

import numpy as np
from compas.typing import IndexGroupsLike
from compas.typing import IndicesLike
from compas.typing import PointsLike
from compas.typing import VerticesFaces

from compas_cgal.booleans import boolean_difference_mesh_mesh
from compas_cgal.booleans import boolean_intersection_mesh_mesh
from compas_cgal.booleans import boolean_union_mesh_mesh
from compas_cgal.intersections import intersection_mesh_mesh
from compas_cgal.meshing import trimesh_dual
from compas_cgal.meshing import trimesh_remesh
from compas_cgal.plugins.booleans import _boolean_difference_mesh_mesh
from compas_cgal.plugins.booleans import _boolean_intersection_mesh_mesh
from compas_cgal.plugins.booleans import _boolean_union_mesh_mesh
from compas_cgal.plugins.intersections import _intersection_mesh_mesh
from compas_cgal.plugins.triangulation import _conforming_delaunay_triangulation
from compas_cgal.plugins.triangulation import _constrained_delaunay_triangulation
from compas_cgal.plugins.triangulation import _delaunay_triangulation
from compas_cgal.plugins.trimesh import _trimesh_slice
from compas_cgal.plugins.trimesh import _trimesh_remesh
from compas_cgal.slicer import slice_mesh_planes


def consume_vertices(value: PointsLike) -> None:
    pass


def consume_faces(value: IndexGroupsLike) -> None:
    pass


def consume_indices(value: IndicesLike) -> None:
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

indices_list = [0, 2]
indices_tuple = (0, 2)
indices_range = range(0, 3, 2)
indices_int32 = np.asarray(indices_list, dtype=np.int32)
indices_int64 = np.asarray(indices_list, dtype=np.int64)

consume_vertices(vertices_list)
consume_vertices(vertices_tuple)
consume_vertices(vertices_float32)
consume_vertices(vertices_float64)
consume_vertices(vertices_int32)
consume_vertices(vertices_int64)
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

consume_indices(indices_list)
consume_indices(indices_tuple)
consume_indices(indices_range)
consume_indices(indices_int32)
consume_indices(indices_int64)

consume_mesh((vertices_list, faces_list))
consume_mesh((vertices_tuple, faces_tuple))
consume_mesh((vertices_float32, faces_int64))
consume_mesh((vertices_fortran, faces_sliced))
consume_mesh((vertices_readonly, faces_readonly))

triangle_mesh: VerticesFaces = (vertices_float32, faces_int64)
boolean_union_mesh_mesh(triangle_mesh, (vertices_fortran, faces_sliced))
boolean_difference_mesh_mesh(triangle_mesh, (vertices_readonly, faces_readonly))
boolean_intersection_mesh_mesh(triangle_mesh, (vertices_list, faces_list))
boolean_union_mesh_mesh((vertices_int32, faces_int64), triangle_mesh)
_boolean_union_mesh_mesh(triangle_mesh, triangle_mesh)
_boolean_difference_mesh_mesh(triangle_mesh, triangle_mesh)
_boolean_intersection_mesh_mesh(triangle_mesh, triangle_mesh)
intersection_mesh_mesh(triangle_mesh, triangle_mesh)
_intersection_mesh_mesh(triangle_mesh, triangle_mesh)
slice_mesh_planes(triangle_mesh, [([0.0, 0.0, 0.0], [0.0, 0.0, 1.0])])
_trimesh_slice(triangle_mesh, [([0.0, 0.0, 0.0], [0.0, 0.0, 1.0])])
trimesh_remesh(triangle_mesh, 0.1)
trimesh_dual(triangle_mesh, fixed_vertices=indices_list)
trimesh_dual(triangle_mesh, fixed_vertices=indices_tuple)
trimesh_dual(triangle_mesh, fixed_vertices=indices_range)
trimesh_dual(triangle_mesh, fixed_vertices=indices_int32)
trimesh_dual(triangle_mesh, fixed_vertices=indices_int64)
_trimesh_remesh(triangle_mesh, 0.1)

domain_float32 = np.asarray(
    [[0.0, 0.0, 0.0], [3.0, 0.0, 0.0], [3.0, 3.0, 0.0], [0.0, 3.0, 0.0]],
    dtype=np.float32,
)
hole_float64 = np.asarray(
    [[[1.0, 1.0, 0.0], [2.0, 1.0, 0.0], [2.0, 2.0, 0.0], [1.0, 2.0, 0.0]]],
    dtype=np.float64,
)
_delaunay_triangulation(vertices_float32)
_delaunay_triangulation(vertices_float64)
_delaunay_triangulation(vertices_int32)
_delaunay_triangulation(vertices_int64)
_constrained_delaunay_triangulation(
    domain_float32,
    holes=hole_float64,
    constraints=np.empty((0, 0, 3), dtype=np.float32),
    points=np.empty((0, 3), dtype=np.float64),
)
_conforming_delaunay_triangulation(domain_float32)
_conforming_delaunay_triangulation(domain_float32, max_edge_length=None)
_conforming_delaunay_triangulation(domain_float32, max_edge_length=np.float64(0.5))
