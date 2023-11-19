from __future__ import annotations
from .types import VerticesFaces, Planes, PolylinesNumpy
import numpy as np
from compas_cgal._cgal import slicer
from compas.plugins import plugin


@plugin(category="trimesh", pluggable_name="trimesh_slice")
def slice_mesh_planes(mesh: VerticesFaces, planes: Planes) -> PolylinesNumpy:
    """Slice a mesh by a list of planes.

    Parameters
    ----------
    mesh : :attr:`compas_cgal.types.VerticesFaces`
        The mesh to slice.
    planes : :attr:`compas_cgal.types.Planes`
        The slicing planes.

    Returns
    -------
    :attr:`compas_cgal.types.PolylinesNumpy`
        A list of slice polylines, with each polyline an array of points.

    Examples
    --------
    >>> from compas.geometry import Sphere, Plane, Polyline
    >>> from compas.utilities import linspace
    >>> from compas_cgal.slicer import slice_mesh

    >>> sphere = Sphere(1.0, point=[0, 0, 1.0])
    >>> mesh = sphere.to_vertices_and_faces(u=32, v=32, triangulated=True)

    >>> planes = [Plane([0, 0, z], [0, 0, 1.0]) for z in linspace(0.1, 1.9, 19)]

    >>> result = slice_mesh(mesh, planes)
    >>> polylines = [Polyline(points) for points in result]

    """
    vertices, faces = mesh
    points, normals = zip(*planes)
    V = np.asarray(vertices, dtype=np.float64)
    F = np.asarray(faces, dtype=np.int32)
    P = np.array(points, dtype=np.float64)
    N = np.array(normals, dtype=np.float64)

    pointsets = slicer.slice_mesh(V, F, P, N)
    return pointsets


slice_mesh = slice_mesh_planes
