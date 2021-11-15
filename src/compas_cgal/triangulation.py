import numpy as np
from compas_cgal._cgal import triangulations


def constrained_delaunay_triangulation(boundary, holes=None, curves=None, maxlength=None):
    """Construct a constrained Delaunay triangulation.

    Parameters
    ----------
    boundary : :class:`compas.geometry.Polygon`
        The boundary of the triangulation.
    holes : list of :class:`compas.geometry.Polygon`, optional
        Internal boundary polygons.
    curves : list of :class:`compas.geometry.Polyline`, optional
        Internal constraint curves.
    maxlength : float, optional
        The maximum length of the triangle edges.

    Returns
    -------
    list
        The vertices and faces of the triangulation.

    Notes
    -----
    ...

    """
    boundary = np.array(boundary, dtype=np.float64)

    if holes:
        holes = [np.array(hole, dtype=np.float64) for hole in holes]
    else:
        holes = []

    if curves:
        curves = [np.array(curve, dtype=np.float64) for curve in curves]
    else:
        curves = []

    maxlength = maxlength or 0.0

    return triangulations.constrained_delaunay_triangulation(boundary, holes, curves, maxlength=maxlength)
