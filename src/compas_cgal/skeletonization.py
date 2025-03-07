import numpy as np
from compas.plugins import plugin

from compas_cgal.compas_cgal_ext import skeletonization

from .types import PolylinesNumpySkeleton
from .types import VerticesFaces


@plugin(category="mesh")
def mesh_skeleton(mesh: VerticesFaces) -> PolylinesNumpySkeleton:
    """Compute the geometric skeleton of a triangle mesh using mean curvature flow.

    Parameters
    ----------
    mesh : VerticesFaces
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
    """
    V, F = mesh
    V = np.asarray(V, dtype=np.float64, order="C")  # Ensure C-contiguous
    F = np.asarray(F, dtype=np.int32, order="C")  # Ensure C-contiguous

    # Get start and end points as flattened vectors
    start_points, end_points = skeletonization.mesh_skeleton(V, F)

    # Convert flattened vectors to list of point coordinates
    edges = []
    for i in range(0, len(start_points), 3):
        start = [start_points[i], start_points[i + 1], start_points[i + 2]]
        end = [end_points[i], end_points[i + 1], end_points[i + 2]]
        edges.append((start, end))

    return edges
