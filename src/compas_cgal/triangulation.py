import numpy as np
from compas.geometry import Point
from compas.plugins import plugin

from compas_cgal.compas_cgal_ext import VectorRowMatrixXd
from compas_cgal.compas_cgal_ext import triangulation
from compas_cgal.types import FacesNumpy
from compas_cgal.types import VerticesFacesNumpy


@plugin(category="triangulation", requires=["compas_cgal"])
def delaunay_triangulation(points: list[Point]) -> FacesNumpy:
    """Construct a Delaunay triangulation from a set of points.

    Parameters
    ----------
    points : list[:class:`compas.geometry.Point`]
        Points of the triangulation.

    Returns
    -------
    :attr:`compas_cgal.types.FacesNumpy`
        The faces of the triangulation.

    Examples
    --------
    >>> from compas.geometry import Pointcloud
    >>> from compas.datastructures import Mesh
    >>> from compas_cgal.triangulation import delaunay_triangulation

    >>> points = Pointcloud.from_bounds(8, 5, 0, 17)
    >>> triangles = delaunay_triangulation(points)

    >>> mesh = Mesh.from_vertices_and_faces(points, triangles)

    """
    vertices = np.asarray(points, dtype=np.float64, order="C")
    return triangulation.delaunay_triangulation(vertices)


@plugin(category="triangulation", requires=["compas_cgal"])
def constrained_delaunay_triangulation(
    boundary,
    points=None,
    holes=None,
    curves=None,
) -> VerticesFacesNumpy:
    """Construct a Constrained Delaunay triangulation.

    Parameters
    ----------
    boundary : :class:`compas.geometry.Polygon`
        The boundary of the triangulation.
    points : list[:class:`compas.geometry.Point`], optional
        Additional internal points.
    holes : list[:class:`compas.geometry.Polygon`], optional
        Internal boundary polygons.
    curves : list[:class:`compas.geometry.Polyline`], optional
        Internal constraint curves.

    Returns
    -------
    :attr:`compas_cgal.types.VerticesFacesNumpy`

    """
    boundary = np.asarray(boundary, dtype=np.float64)

    points = points or []
    points = np.asarray(points, dtype=np.float64, order="C")

    holes_vector = VectorRowMatrixXd()
    if holes:
        for hole in holes:
            hole_array = np.asarray(hole, dtype=np.float64, order="C")
            holes_vector.append(hole_array)

    curves_vector = VectorRowMatrixXd()
    if curves:
        for curve in curves:
            curve_array = np.asarray(curve, dtype=np.float64, order="C")
            curves_vector.append(curve_array)

    return triangulation.constrained_delaunay_triangulation(
        boundary,  # numpy array
        points,  # numpy array
        holes_vector,  # VectorRowMatrixXd
        curves_vector,  # VectorRowMatrixXd
        False,  # is_conforming=False
    )


@plugin(category="triangulation", requires=["compas_cgal"])
def conforming_delaunay_triangulation(
    boundary,
    points=None,
    holes=None,
    curves=None,
) -> VerticesFacesNumpy:
    """Construct a Conforming Delaunay triangulation.

    Parameters
    ----------
    boundary : :class:`compas.geometry.Polygon`
        The boundary of the triangulation.
    points : list[:class:`compas.geometry.Point`], optional
        Additional internal points.
    holes : list[:class:`compas.geometry.Polygon`], optional
        Internal boundary polygons.
    curves : list[:class:`compas.geometry.Polyline`], optional
        Internal constraint curves.

    Returns
    -------
    :attr:`compas_cgal.types.VerticesFacesNumpy`

    """
    # Convert boundary to numpy array
    boundary = np.asarray(boundary, dtype=np.float64, order="C")

    # Handle points parameter
    if points is None:
        points = np.zeros((0, 3), dtype=np.float64, order="C")
    else:
        points = np.asarray(points, dtype=np.float64, order="C")

    # Convert holes to numpy arrays and create vector
    holes_vector = VectorRowMatrixXd()
    if holes:
        for hole in holes:
            if len(hole) < 3:
                continue
            hole_array = np.asarray(hole, dtype=np.float64, order="C")
            holes_vector.append(hole_array)

    # Create empty vector for curves
    curves_vector = VectorRowMatrixXd()

    if curves:
        for curve in curves:
            curve_array = np.asarray(curve, dtype=np.float64, order="C")
            curves_vector.append(curve_array)

    # Call C++ function with all required arguments
    result = triangulation.constrained_delaunay_triangulation(
        boundary,  # numpy array
        points,  # numpy array
        holes_vector,  # VectorRefRowMatrixXd
        curves_vector,  # VectorRefRowMatrixXd
        True,  # is_conforming=True
    )

    return result


def refined_delaunay_mesh(
    boundary,
    points=None,
    holes=None,
    curves=None,
    maxlength=None,
    is_optimized=False,
) -> VerticesFacesNumpy:
    """Construct a refined Delaunay mesh.

    Parameters
    ----------
    boundary : :class:`compas.geometry.Polygon`
        The boundary of the triangulation.
    points : list[:class:`compas.geometry.Point`], optional
        Additional internal points.
    holes : list[:class:`compas.geometry.Polygon`], optional
        Internal boundary polygons.
    curves : list[:class:`compas.geometry.Polyline`], optional
        Internal constraint curves.
    maxlength : float, optional
        The maximum length of the triangle edges.
    is_optimized : bool, optional
        Apply LLoyd's optimisation [1]_.

    Returns
    -------
    :attr:`compas_cgal.types.VerticesFacesNumpy`

    References
    ----------
    .. [1] https://doc.cgal.org/latest/Mesh_2/index.html#secMesh_2_meshes

    """
    boundary = np.asarray(boundary, dtype=np.float64, order="C")

    # Handle points parameter
    if points is None:
        points = np.zeros((0, 2), dtype=np.float64, order="C")  # 2D points for triangulation
    else:
        points = np.asarray(points, dtype=np.float64, order="C")

    # Create vectors for holes and curves with proper type conversion
    holes_vector = VectorRowMatrixXd()
    if holes:
        for hole in holes:
            if len(hole) < 3:
                continue
            hole_array = np.asarray(hole, dtype=np.float64, order="C")
            holes_vector.append(hole_array)

    curves_vector = VectorRowMatrixXd()
    if curves:
        for curve in curves:
            curve_array = np.asarray(curve, dtype=np.float64, order="C")
            curves_vector.append(curve_array)

    maxlength = maxlength or 0.0

    # Call C++ function with proper type conversion and parameter order
    return triangulation.refined_delaunay_mesh(
        boundary,  # B: numpy array (Nx2)
        points,  # P: numpy array (Mx2)
        holes_vector,  # holes: VectorRowMatrixXd
        curves_vector,  # curves: VectorRowMatrixXd
        0.0,  # minangle: float
        maxlength,  # maxlength: float
        is_optimized,  # is_optimized: bool
    )
