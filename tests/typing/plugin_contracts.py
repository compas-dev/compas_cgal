"""Static consumer coverage for every CGAL plugin registration family."""

from collections.abc import Sequence
from typing import assert_type

from compas.geometry import Plane
from compas.typing import PointsLike
from compas.typing import VerticesFaces

from compas_cgal.plugins.booleans import _boolean_difference_mesh_mesh
from compas_cgal.plugins.booleans import _boolean_intersection_mesh_mesh
from compas_cgal.plugins.booleans import _boolean_union_mesh_mesh
from compas_cgal.plugins.intersections import _intersection_mesh_mesh
from compas_cgal.plugins.triangulation import _conforming_delaunay_triangulation
from compas_cgal.plugins.triangulation import _constrained_delaunay_triangulation
from compas_cgal.plugins.triangulation import _delaunay_triangulation
from compas_cgal.plugins.trimesh import _trimesh_remesh
from compas_cgal.plugins.trimesh import _trimesh_slice
from compas_cgal.types import PolylinesNumpy
from compas_cgal.types import VerticesFacesNumpy


def check_plugin_contracts(
    mesh: VerticesFaces,
    points: PointsLike,
    planes: Sequence[Plane],
) -> None:
    assert_type(_boolean_union_mesh_mesh(mesh, mesh), VerticesFacesNumpy)
    assert_type(_boolean_difference_mesh_mesh(mesh, mesh), VerticesFacesNumpy)
    assert_type(_boolean_intersection_mesh_mesh(mesh, mesh), VerticesFacesNumpy)
    assert_type(_intersection_mesh_mesh(mesh, mesh), PolylinesNumpy)
    assert_type(_delaunay_triangulation(points), VerticesFaces)
    assert_type(_constrained_delaunay_triangulation(points), VerticesFaces)
    assert_type(_conforming_delaunay_triangulation(points), VerticesFaces)
    assert_type(_conforming_delaunay_triangulation(points, max_edge_length=None), VerticesFaces)
    assert_type(_conforming_delaunay_triangulation(points, max_edge_length=1.0), VerticesFaces)
    assert_type(_trimesh_remesh(mesh, 1.0), VerticesFacesNumpy)
    assert_type(_trimesh_slice(mesh, planes), PolylinesNumpy)
