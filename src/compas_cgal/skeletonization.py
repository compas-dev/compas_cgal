from compas.typing import VerticesFaces

from compas_cgal import _skeletonization
from compas_cgal import _types_std  # noqa: F401

from ._mesh import as_native_mesh
from .types import PolylinesNumpySkeleton
from .types import SkeletonVertexMapping

__all__ = ["mesh_skeleton", "mesh_skeleton_with_mapping"]


def _validate_skeleton_result(result, operation):
    """Check paired native skeleton vectors without asserting numerical correctness."""
    if len(result) != 4:
        raise RuntimeError(f"CGAL {operation} should return start points, end points, and two vertex mappings.")
    start_points, end_points, start_vertex_indices, end_vertex_indices = result
    if len(start_points) != len(end_points) or len(start_points) % 3:
        raise RuntimeError(f"CGAL {operation} should return equally sized XYZ start and end point vectors.")
    edge_count = len(start_points) // 3
    if len(start_vertex_indices) != edge_count or len(end_vertex_indices) != edge_count:
        raise RuntimeError(f"CGAL {operation} returned {edge_count} edges, {len(start_vertex_indices)} start mappings, and {len(end_vertex_indices)} end mappings.")
    return result


def mesh_skeleton(mesh: VerticesFaces) -> PolylinesNumpySkeleton:
    """Compute the geometric skeleton of a triangle mesh using mean curvature flow.

    Parameters
    ----------
    mesh
        A tuple containing:
        * vertices: Nx3 array of vertex coordinates
        * faces: Mx3 array of vertex indices

    Returns
    -------
    PolylinesNumpySkeleton
        List of polylines representing the skeleton edges.
        Each polyline is a tuple of start and end point coordinates.

    Raises
    ------
    TypeError
        If the input mesh is not a tuple of vertices and faces.
    ValueError
        If the vertices array is not Nx3.
        If the faces array is not Mx3.
        If the face indices are out of range.
        If the mesh is not manifold and closed.
    RuntimeError
        If the mesh contraction fails to converge.

    Notes
    -----
    The input mesh must be manifold and closed.
    The skeleton is computed using mean curvature flow.

    Warnings
    --------
    Skeletonization results are currently known to be geometrically incorrect
    for some inputs. Treat this operation as experimental; the return type
    describes the data contract, not the correctness of the result.
    """
    V_numpy, F_numpy = as_native_mesh(mesh, "mesh")

    # Get start and end points as flattened vectors
    start_points, end_points, _, _ = _validate_skeleton_result(_skeletonization.mesh_skeleton(V_numpy, F_numpy), "mesh skeletonization")

    # Convert flattened vectors to list of point coordinates
    edges = []
    for i in range(0, len(start_points), 3):
        start = [start_points[i], start_points[i + 1], start_points[i + 2]]
        end = [end_points[i], end_points[i + 1], end_points[i + 2]]
        edges.append((start, end))

    return edges


def mesh_skeleton_with_mapping(mesh: VerticesFaces) -> tuple[PolylinesNumpySkeleton, SkeletonVertexMapping]:
    """Compute the geometric skeleton of a triangle mesh with vertex correspondence mapping.

    Parameters
    ----------
    mesh
        A tuple containing:
        * vertices: Nx3 array of vertex coordinates
        * faces: Mx3 array of vertex indices

    Returns
    -------
    PolylinesSkeletonWithMapping
        A tuple containing:
        * edges: List of polylines representing the skeleton edges.
          Each polyline is a tuple of start and end point coordinates.
        * vertex_indices: List of tuples, each containing two lists of
          vertex indices corresponding to the start and end vertices of
          each skeleton edge. These are the original mesh vertices that
          contracted to form each skeleton vertex.

    Raises
    ------
    TypeError
        If the input mesh is not a tuple of vertices and faces.
    ValueError
        If the vertices array is not Nx3.
        If the faces array is not Mx3.
        If the face indices are out of range.
        If the mesh is not manifold and closed.
    RuntimeError
        If the mesh contraction fails to converge.

    Notes
    -----
    The input mesh must be manifold and closed.
    The skeleton is computed using mean curvature flow.
    Each skeleton vertex corresponds to a set of original mesh vertices
    that were contracted to that point during the skeletonization process.
    (The set might be empty for some skeleton vertices that don't correspond
    to any original vertex.)

    Warnings
    --------
    Skeletonization results are currently known to be geometrically incorrect
    for some inputs. Treat this operation as experimental; the return type
    describes the data contract, not the correctness of the result.

    """
    V_numpy, F_numpy = as_native_mesh(mesh, "mesh")

    # Get start and end points and vertex indices
    start_points, end_points, start_vertex_indices, end_vertex_indices = _validate_skeleton_result(
        _skeletonization.mesh_skeleton(V_numpy, F_numpy),
        "mesh skeletonization with mapping",
    )

    # Convert flattened vectors to list of point coordinates
    edges = []
    vertex_indices = []

    for i in range(0, len(start_points), 3):
        start = [start_points[i], start_points[i + 1], start_points[i + 2]]
        end = [end_points[i], end_points[i + 1], end_points[i + 2]]
        edges.append((start, end))

    # Process vertex indices - convert VectorInt to Python lists
    for start_indices, end_indices in zip(start_vertex_indices, end_vertex_indices):
        vertex_indices.append((list(start_indices), list(end_indices)))

    return edges, vertex_indices
