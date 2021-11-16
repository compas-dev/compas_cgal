import numpy as np
from compas_cgal._cgal import triangulations


def delaunay_triangulation(vertices):
    """Construct a Delaunay triangulation.

    Parameters
    ----------
    vertices : list of :class:`compas.geometry.Point`
        Vertices of the triangulation.

    Returns
    -------
    list
        The faces of the triangulation.

    Notes
    -----
    ...

    """
    vertices = np.asarray(vertices, dtype=np.float64)
    return triangulations.delaunay_triangulation(vertices)


def constrained_delaunay_triangulation(boundary, points=None, holes=None, curves=None):
    """Construct a Constrained Delaunay triangulation.

    Parameters
    ----------
    boundary : :class:`compas.geometry.Polygon`
        The boundary of the triangulation.
    points : list of :class:`compas.geometry.Point`, optional
        Additional internal points.
    holes : list of :class:`compas.geometry.Polygon`, optional
        Internal boundary polygons.
    curves : list of :class:`compas.geometry.Polyline`, optional
        Internal constraint curves.

    Returns
    -------
    list
        The vertices and faces of the triangulation.

    Notes
    -----
    ...

    """
    boundary = np.asarray(boundary, dtype=np.float64)

    points = points or []
    points = np.asarray(points, dtype=np.float64)

    if holes:
        holes = [np.asarray(hole, dtype=np.float64) for hole in holes]
    else:
        holes = []

    if curves:
        curves = [np.asarray(curve, dtype=np.float64) for curve in curves]
    else:
        curves = []

    return triangulations.constrained_delaunay_triangulation(boundary, points, holes, curves, is_conforming=False)


def conforming_delaunay_triangulation(boundary, points=None, holes=None, curves=None):
    """Construct a Conforming Delaunay triangulation.

    Parameters
    ----------
    boundary : :class:`compas.geometry.Polygon`
        The boundary of the triangulation.
    points : list of :class:`compas.geometry.Point`, optional
        Additional internal points.
    holes : list of :class:`compas.geometry.Polygon`, optional
        Internal boundary polygons.
    curves : list of :class:`compas.geometry.Polyline`, optional
        Internal constraint curves.

    Returns
    -------
    list
        The vertices and faces of the triangulation.

    Notes
    -----
    ...

    """
    boundary = np.asarray(boundary, dtype=np.float64)

    points = points or []
    points = np.asarray(points, dtype=np.float64)

    if holes:
        holes = [np.asarray(hole, dtype=np.float64) for hole in holes]
    else:
        holes = []

    if curves:
        curves = [np.asarray(curve, dtype=np.float64) for curve in curves]
    else:
        curves = []

    return triangulations.constrained_delaunay_triangulation(boundary, points, holes, curves, is_conforming=True)


def refined_delaunay_mesh(boundary, points=None, holes=None, curves=None, maxlength=None, is_optimized=False):
    """Construct a refined Delaunay mesh.

    Parameters
    ----------
    boundary : :class:`compas.geometry.Polygon`
        The boundary of the triangulation.
    points : list of :class:`compas.geometry.Point`, optional
        Additional internal points.
    holes : list of :class:`compas.geometry.Polygon`, optional
        Internal boundary polygons.
    curves : list of :class:`compas.geometry.Polyline`, optional
        Internal constraint curves.
    maxlength : float, optional
        The maximum length of the triangle edges.
    is_optimized : bool, optional
        Apply LLoyd's optimisation.

    Returns
    -------
    list
        The vertices and faces of the triangulation.

    Notes
    -----
    ...

    """
    boundary = np.asarray(boundary, dtype=np.float64)

    points = points or []
    points = np.asarray(points, dtype=np.float64)

    if holes:
        holes = [np.asarray(hole, dtype=np.float64) for hole in holes]
    else:
        holes = []

    if curves:
        curves = [np.asarray(curve, dtype=np.float64) for curve in curves]
    else:
        curves = []

    maxlength = maxlength or 0.0

    return triangulations.refined_delaunay_mesh(boundary, points, holes, curves, maxlength=maxlength, is_optimized=is_optimized)
