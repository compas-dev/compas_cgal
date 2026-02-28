"""Isoline extraction from vertex scalar fields using CGAL."""

from typing import List

import numpy as np
from compas.datastructures import Mesh
from numpy.typing import NDArray

from compas_cgal._isolines import isolines as _isolines
from compas_cgal.types import PolylinesNumpy

__all__ = ["isolines"]


def _smooth_polyline(pts: NDArray, iterations: int = 1) -> NDArray:
    """Apply Laplacian smoothing to a polyline, keeping endpoints fixed."""
    if len(pts) < 3:
        return pts
    smoothed = pts.copy()
    for _ in range(iterations):
        new_pts = smoothed.copy()
        for i in range(1, len(pts) - 1):
            new_pts[i] = (smoothed[i - 1] + smoothed[i + 1]) / 2
        smoothed = new_pts
    return smoothed


def _segment_lengths(pts: NDArray) -> NDArray:
    """Compute segment lengths for a polyline."""
    return np.linalg.norm(np.diff(pts, axis=0), axis=1)


def _resample_polyline_adaptive(pts: NDArray, threshold: float = 2.0) -> NDArray:
    """Resample only segments significantly longer than median.

    Parameters
    ----------
    pts : NDArray
        Polyline points (Nx3).
    threshold : float
        Segments longer than threshold * median_length get subdivided.

    Returns
    -------
    NDArray
        Resampled polyline.
    """
    if len(pts) < 3:
        return pts

    lengths = _segment_lengths(pts)
    median_len = np.median(lengths)

    if median_len == 0:
        return pts

    result = [pts[0]]
    for i in range(len(pts) - 1):
        p0, p1 = pts[i], pts[i + 1]
        seg_len = lengths[i]

        # subdivide long segments proportionally
        if seg_len > threshold * median_len:
            n_subdivs = int(np.ceil(seg_len / median_len))
            for j in range(1, n_subdivs):
                t = j / n_subdivs
                result.append(p0 * (1 - t) + p1 * t)

        result.append(p1)

    return np.array(result)


def _resample_polyline(pts: NDArray, factor: int) -> NDArray:
    """Resample a polyline by inserting interpolated points between each pair."""
    if len(pts) < 2 or factor < 2:
        return pts
    result = [pts[0]]
    for i in range(len(pts) - 1):
        p0, p1 = pts[i], pts[i + 1]
        for j in range(1, factor):
            t = j / factor
            result.append(p0 * (1 - t) + p1 * t)
        result.append(p1)
    return np.array(result)


def isolines(
    mesh: Mesh,
    scalars: str,
    isovalues: List[float] | None = None,
    n: int | None = None,
    resample: int | bool = True,
    smoothing: int = 0,
) -> PolylinesNumpy:
    """Extract isoline polylines from vertex scalar field.

    Uses CGAL's refine_mesh_at_isolevel to extract isolines from a scalar
    field defined at mesh vertices.

    Parameters
    ----------
    mesh : :class:`compas.datastructures.Mesh`
        A triangulated mesh.
    scalars : str
        Name of the vertex attribute containing scalar values.
    isovalues : List[float], optional
        Explicit isovalue thresholds for isoline extraction.
    n : int, optional
        Number of evenly spaced isovalues between scalar min and max.
        The isovalues will exclude the endpoints.
    resample : int or bool, optional
        Polyline resampling mode. If True (default), adaptively resample
        segments longer than 2x median length. If int > 1, uniformly
        subdivide each segment into that many parts. If False or 1, disable.
    smoothing : int, optional
        Number of Laplacian smoothing iterations to apply to polylines.
        Default is 0 (no smoothing).

    Returns
    -------
    :attr:`compas_cgal.types.PolylinesNumpy`
        List of polyline segments as Nx3 arrays of points.

    Raises
    ------
    ValueError
        If neither or both of `isovalues` and `n` are provided.

    Examples
    --------
    >>> from compas.datastructures import Mesh
    >>> from compas.geometry import Sphere
    >>> from compas_cgal.geodesics import heat_geodesic_distances
    >>> from compas_cgal.isolines import isolines
    >>> sphere = Sphere(1.0)
    >>> mesh = Mesh.from_shape(sphere, u=32, v=32)
    >>> mesh.quads_to_triangles()
    >>> vf = mesh.to_vertices_and_faces()
    >>> distances = heat_geodesic_distances(vf, [0])
    >>> for key, d in zip(mesh.vertices(), distances):
    ...     mesh.vertex_attribute(key, "distance", d)
    >>> polylines = isolines(mesh, "distance", n=5)

    """
    V = np.asarray(mesh.vertices_attributes("xyz"), dtype=np.float64, order="C")
    F = np.asarray([mesh.face_vertices(f) for f in mesh.faces()], dtype=np.int32, order="C")
    scalar_values = np.asarray(mesh.vertices_attribute(scalars), dtype=np.float64, order="C").reshape(-1, 1)

    if isovalues is None and n is None:
        raise ValueError("provide isovalues or n")
    if isovalues is not None and n is not None:
        raise ValueError("provide isovalues or n, not both")

    if n is not None:
        smin, smax = float(scalar_values.min()), float(scalar_values.max())
        isovalues = np.linspace(smin, smax, n + 2)[1:-1].tolist()

    polylines = list(_isolines(V, F, scalar_values, isovalues, 0))

    if resample is True:
        polylines = [_resample_polyline_adaptive(pl) for pl in polylines]
    elif isinstance(resample, int) and resample > 1:
        polylines = [_resample_polyline(pl, resample) for pl in polylines]

    if smoothing > 0:
        polylines = [_smooth_polyline(pl, smoothing) for pl in polylines]

    return polylines
