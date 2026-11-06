"""Static result coverage for every public CGAL wrapper family."""

from collections.abc import Sequence
from typing import Literal
from typing import assert_type

from compas.datastructures import Graph
from compas.datastructures import Mesh
from compas.geometry import Line
from compas.geometry import Plane
from compas.geometry import Polygon
from compas.geometry import PolygonalSurface
from compas.geometry import Polyhedron
from compas.typing import Float64Array
from compas.typing import Int32Array
from compas.typing import PointsLike
from compas.typing import VerticesFaces

from compas_cgal.booleans import boolean_chain
from compas_cgal.booleans import boolean_chain_with_face_source
from compas_cgal.booleans import boolean_difference_mesh_mesh
from compas_cgal.booleans import boolean_difference_mesh_mesh_with_edges
from compas_cgal.booleans import boolean_difference_mesh_mesh_with_face_source
from compas_cgal.booleans import boolean_difference_mesh_meshes
from compas_cgal.booleans import boolean_intersection_mesh_mesh
from compas_cgal.booleans import boolean_intersection_mesh_mesh_with_edges
from compas_cgal.booleans import boolean_intersection_mesh_mesh_with_face_source
from compas_cgal.booleans import boolean_union_mesh_mesh
from compas_cgal.booleans import boolean_union_mesh_mesh_with_edges
from compas_cgal.booleans import boolean_union_mesh_mesh_with_face_source
from compas_cgal.booleans import split_by_source
from compas_cgal.booleans import split_mesh_mesh
from compas_cgal.geodesics import ExactGeodesicSolver
from compas_cgal.geodesics import HeatGeodesicSolver
from compas_cgal.geodesics import exact_geodesic_distances
from compas_cgal.geodesics import exact_geodesic_distances_from_points
from compas_cgal.geodesics import geodesic_isolines
from compas_cgal.geodesics import geodesic_isolines_split
from compas_cgal.geodesics import heat_geodesic_distances
from compas_cgal.intersections import intersection_mesh_mesh
from compas_cgal.isolines import isolines
from compas_cgal.measure import mesh_area
from compas_cgal.measure import mesh_centroid
from compas_cgal.measure import mesh_volume
from compas_cgal.meshing import trimesh_dual
from compas_cgal.meshing import trimesh_remesh
from compas_cgal.polylines import closest_points_on_polyline
from compas_cgal.polylines import simplify_polyline
from compas_cgal.polylines import simplify_polylines
from compas_cgal.projection import project_mesh_on_mesh
from compas_cgal.projection import project_points_on_mesh
from compas_cgal.projection import pull_mesh_on_mesh
from compas_cgal.projection import pull_points_on_mesh
from compas_cgal.reconstruction import pointset_normal_estimation
from compas_cgal.reconstruction import pointset_outlier_removal
from compas_cgal.reconstruction import pointset_reduction
from compas_cgal.reconstruction import pointset_smoothing
from compas_cgal.reconstruction import poisson_surface_reconstruction
from compas_cgal.skeletonization import mesh_skeleton
from compas_cgal.skeletonization import mesh_skeleton_with_mapping
from compas_cgal.slicer import slice_mesh_planes
from compas_cgal.straight_skeleton_2 import extrude
from compas_cgal.straight_skeleton_2 import graph_from_skeleton_data
from compas_cgal.straight_skeleton_2 import interior_straight_skeleton
from compas_cgal.straight_skeleton_2 import interior_straight_skeleton_with_holes
from compas_cgal.straight_skeleton_2 import offset_polygon
from compas_cgal.straight_skeleton_2 import offset_polygon_with_holes
from compas_cgal.straight_skeleton_2 import weighted_offset_polygon
from compas_cgal.subdivision import mesh_subdivide_catmull_clark
from compas_cgal.subdivision import mesh_subdivide_loop
from compas_cgal.subdivision import mesh_subdivide_sqrt3
from compas_cgal.triangulation import conforming_delaunay_triangulation
from compas_cgal.triangulation import constrained_delaunay_triangulation
from compas_cgal.triangulation import delaunay_triangulation
from compas_cgal.types import DualMeshNumpy
from compas_cgal.types import DelaunayResult
from compas_cgal.types import FloatNx3
from compas_cgal.types import IntNx2
from compas_cgal.types import IntNx3
from compas_cgal.types import PolylinesNumpy
from compas_cgal.types import PolylinesNumpySkeleton
from compas_cgal.types import SkeletonData
from compas_cgal.types import SkeletonVertexMapping
from compas_cgal.types import VerticesFacesEdgesNumpy
from compas_cgal.types import VerticesFacesNumpy
from compas_cgal.types import VerticesFacesSourceNumpy
from compas_cgal.types import VerticesQuadsNumpy


def check_public_results(
    mesh: Mesh,
    mesh_data: VerticesFaces,
    vertices: FloatNx3,
    faces: IntNx3,
    edges: IntNx2,
    points: PointsLike,
    planes: Sequence[Plane],
) -> None:
    boolean_operations: list[Literal["union", "difference", "intersection", "xor"]] = ["union"]
    source_operations: list[Literal["union", "difference", "intersection"]] = ["union"]

    boolean_result = boolean_union_mesh_mesh(mesh_data, mesh_data)
    assert_type(boolean_result, VerticesFacesNumpy)
    Mesh.from_vertices_and_faces(*boolean_result)
    Polyhedron(*boolean_result)
    assert_type(boolean_difference_mesh_mesh(mesh_data, mesh_data), VerticesFacesNumpy)
    assert_type(boolean_intersection_mesh_mesh(mesh_data, mesh_data), VerticesFacesNumpy)
    assert_type(split_mesh_mesh(mesh_data, mesh_data), VerticesFacesNumpy)
    assert_type(boolean_union_mesh_mesh_with_edges(mesh_data, mesh_data), VerticesFacesEdgesNumpy)
    assert_type(boolean_difference_mesh_mesh_with_edges(mesh_data, mesh_data), VerticesFacesEdgesNumpy)
    assert_type(boolean_intersection_mesh_mesh_with_edges(mesh_data, mesh_data), VerticesFacesEdgesNumpy)
    assert_type(boolean_union_mesh_mesh_with_face_source(mesh_data, mesh_data), VerticesFacesSourceNumpy)
    assert_type(boolean_difference_mesh_mesh_with_face_source(mesh_data, mesh_data), VerticesFacesSourceNumpy)
    assert_type(boolean_intersection_mesh_mesh_with_face_source(mesh_data, mesh_data), VerticesFacesSourceNumpy)
    assert_type(boolean_chain([mesh_data, mesh_data], boolean_operations), VerticesFacesNumpy)
    assert_type(boolean_chain_with_face_source([mesh_data, mesh_data], source_operations), VerticesFacesSourceNumpy)
    assert_type(boolean_difference_mesh_meshes(mesh_data, [mesh_data]), VerticesFacesNumpy)
    assert_type(split_by_source(vertices, faces, edges), dict[int, VerticesFacesNumpy])

    assert_type(heat_geodesic_distances(mesh_data, [0]), Float64Array)
    assert_type(geodesic_isolines_split(mesh_data, [0], [0.5]), list[VerticesFacesNumpy])
    assert_type(geodesic_isolines(mesh_data, [0], [0.5]), PolylinesNumpy)
    assert_type(exact_geodesic_distances(mesh_data, [0]), Float64Array)
    assert_type(exact_geodesic_distances(mesh_data, [0], return_sources=True), tuple[Float64Array, Int32Array])
    assert_type(exact_geodesic_distances_from_points(mesh_data, points), Float64Array)
    assert_type(exact_geodesic_distances_from_points(mesh_data, points, return_sources=True), tuple[Float64Array, Int32Array])
    heat_solver = HeatGeodesicSolver(mesh_data)
    assert_type(heat_solver.solve([0]), Float64Array)
    exact_solver = ExactGeodesicSolver(mesh_data)
    assert_type(exact_solver.solve([0]), Float64Array)
    assert_type(exact_solver.solve_from_points(points), Float64Array)

    assert_type(intersection_mesh_mesh(mesh_data, mesh_data), PolylinesNumpy)
    assert_type(isolines(mesh, [0.0], isovalues=[0.5]), PolylinesNumpy)
    assert_type(isolines(mesh, vertices[:, 0], isovalues=[0.5]), PolylinesNumpy)
    assert_type(mesh_area(mesh_data), float)
    assert_type(mesh_volume(mesh_data), float)
    assert_type(mesh_centroid(mesh_data), list[float])
    assert_type(trimesh_remesh(mesh_data, 1.0), VerticesFacesNumpy)
    assert_type(trimesh_dual(mesh_data), DualMeshNumpy)
    assert_type(simplify_polylines([points], 0.1), PolylinesNumpy)
    assert_type(simplify_polyline(points, 0.1), Float64Array)
    assert_type(closest_points_on_polyline(points, points), Float64Array)

    assert_type(project_mesh_on_mesh(mesh, mesh), Mesh)
    assert_type(pull_mesh_on_mesh(mesh, mesh), Mesh)
    assert_type(project_points_on_mesh(points, mesh), FloatNx3)
    assert_type(pull_points_on_mesh(points, points, mesh), FloatNx3)
    assert_type(poisson_surface_reconstruction(points, points), VerticesFacesNumpy)
    assert_type(pointset_outlier_removal(points), FloatNx3)
    assert_type(pointset_reduction(points), FloatNx3)
    assert_type(pointset_smoothing(points), FloatNx3)
    assert_type(pointset_normal_estimation(points), tuple[FloatNx3, FloatNx3])

    assert_type(mesh_skeleton(mesh_data), PolylinesNumpySkeleton)
    assert_type(mesh_skeleton_with_mapping(mesh_data), tuple[PolylinesNumpySkeleton, SkeletonVertexMapping])
    assert_type(slice_mesh_planes(mesh_data, planes), PolylinesNumpy)
    assert_type(graph_from_skeleton_data(vertices, [0], edges, [0]), Graph)
    assert_type(interior_straight_skeleton(points), Graph)
    assert_type(interior_straight_skeleton(points, as_graph=False), SkeletonData)
    assert_type(interior_straight_skeleton_with_holes(points, [points]), Graph)
    assert_type(interior_straight_skeleton_with_holes(points, [points], as_graph=False), SkeletonData)
    assert_type(offset_polygon(points, 1.0), list[Polygon])
    assert_type(offset_polygon_with_holes(points, [points], 1.0), list[tuple[Polygon, list[Polygon]]])
    assert_type(weighted_offset_polygon(points, 1.0, [1.0]), list[Polygon])
    assert_type(extrude(points), tuple[Mesh, list[Line]])
    assert_type(mesh_subdivide_catmull_clark(mesh_data), VerticesQuadsNumpy)
    assert_type(mesh_subdivide_loop(mesh_data), VerticesFacesNumpy)
    assert_type(mesh_subdivide_sqrt3(mesh_data), VerticesFacesNumpy)
    delaunay_result = delaunay_triangulation(points)
    assert_type(delaunay_result, DelaunayResult)
    PolygonalSurface(*delaunay_result)
    assert_type(constrained_delaunay_triangulation(points), DelaunayResult)
    assert_type(conforming_delaunay_triangulation(points), DelaunayResult)
    assert_type(conforming_delaunay_triangulation(points, max_edge_length=None), DelaunayResult)
    assert_type(conforming_delaunay_triangulation(points, max_edge_length=1.0), DelaunayResult)
