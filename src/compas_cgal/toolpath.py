"""Trochoidal toolpath generation from polygon MAT samples (CGAL backend)."""

import math
from dataclasses import dataclass

import numpy as np
from compas.geometry import Arc
from compas.geometry import Circle
from compas.geometry import Frame
from compas.geometry import Line
from compas.geometry import Polygon
from compas.geometry import normal_polygon
from compas.tolerance import TOL

from compas_cgal import _toolpath  # type: ignore
from compas_cgal import _types_std  # noqa: F401  # type: ignore
from compas_cgal.types import PolylinesNumpy

__all__ = [
    "ToolpathOperation",
    "polygon_medial_axis_transform",
    "trochoidal_mat_toolpath",
    "trochoidal_mat_toolpath_circular",
]

_OPERATION_NAMES = ("cut", "lead_in", "lead_out", "link", "retract", "plunge")


@dataclass
class ToolpathOperation:
    """A single toolpath motion primitive with operation metadata."""

    geometry: Line | Arc | Circle
    operation: str
    path_index: int


def _polygon_to_ccw_vertices(polygon: Polygon) -> np.ndarray:
    pts = np.asarray(polygon.points, dtype=np.float64)
    if pts.ndim != 2 or pts.shape[0] < 3:
        raise ValueError("Expected a polygon with at least three points.")

    if pts.shape[1] == 2:
        pts = np.column_stack((pts, np.zeros(len(pts), dtype=np.float64)))
    elif pts.shape[1] != 3:
        raise ValueError("Expected points with shape Nx2 or Nx3.")

    if np.allclose(pts[0], pts[-1]):
        pts = pts[:-1]

    normal = normal_polygon(pts.tolist(), True)
    if TOL.is_allclose(normal, [0, 0, -1]):
        pts = pts[::-1]
        normal = [0.0, 0.0, 1.0]

    if not TOL.is_allclose(normal, [0, 0, 1]):
        raise ValueError("Polygon should lie in XY plane with upward normal [0, 0, 1].")

    return np.asarray(pts, dtype=np.float64, order="C")


def _unit_xy_3(v: np.ndarray) -> np.ndarray | None:
    """Unit vector in XY from *v*, with z=0. None when degenerate."""
    norm = math.hypot(float(v[0]), float(v[1]))
    if norm <= TOL.absolute:
        return None
    inv = 1.0 / norm
    return np.array([float(v[0]) * inv, float(v[1]) * inv, 0.0], dtype=np.float64)


def _ccw_angle_xy(u: np.ndarray, v: np.ndarray) -> float:
    """CCW angle from *u* to *v* in [0, 2π)."""
    angle = math.atan2(
        float(u[0]) * float(v[1]) - float(u[1]) * float(v[0]),
        float(u[0]) * float(v[0]) + float(u[1]) * float(v[1]),
    )
    return angle + 2.0 * math.pi if angle < 0.0 else angle


def _row_to_line(start: np.ndarray, end: np.ndarray) -> Line:
    return Line(start.tolist(), end.tolist())


def _row_to_arc(start: np.ndarray, end: np.ndarray, center: np.ndarray, radius: float, clockwise: bool) -> Arc | None:
    start_vector = _unit_xy_3(start - center)
    end_vector = _unit_xy_3(end - center)
    if start_vector is None or end_vector is None:
        return None

    if clockwise:
        xaxis = end_vector
        yaxis = np.array([-xaxis[1], xaxis[0], 0.0], dtype=np.float64)
        start_angle = _ccw_angle_xy(xaxis, start_vector)
        end_angle = 0.0
    else:
        xaxis = start_vector
        yaxis = np.array([-xaxis[1], xaxis[0], 0.0], dtype=np.float64)
        start_angle = 0.0
        end_angle = _ccw_angle_xy(xaxis, end_vector)

    frame = Frame(center.tolist(), xaxis.tolist(), yaxis.tolist())
    return Arc(radius, start_angle, end_angle, frame=frame)


def _row_to_circle(center: np.ndarray, start: np.ndarray, radius: float) -> Circle | None:
    xaxis = _unit_xy_3(start - center)
    if xaxis is None:
        return None
    yaxis = np.array([-xaxis[1], xaxis[0], 0.0], dtype=np.float64)
    frame = Frame(center.tolist(), xaxis.tolist(), yaxis.tolist())
    return Circle(radius, frame=frame)


def _matrices_to_operations(
    meta: np.ndarray,
    starts: np.ndarray,
    ends: np.ndarray,
    centers: np.ndarray,
    radii: np.ndarray,
) -> list[ToolpathOperation]:
    ops: list[ToolpathOperation] = []
    for i in range(meta.shape[0]):
        path_index = int(meta[i, 0])
        ptype = int(meta[i, 1])
        clockwise = bool(meta[i, 2] > 0.5)
        operation = _OPERATION_NAMES[int(meta[i, 3])]

        if ptype == 0:
            geom = _row_to_line(starts[i], ends[i])
        elif ptype == 1:
            geom = _row_to_arc(starts[i], ends[i], centers[i], float(radii[i]), clockwise)
        else:
            geom = _row_to_circle(centers[i], starts[i], float(radii[i]))

        if geom is not None:
            ops.append(ToolpathOperation(geometry=geom, operation=operation, path_index=path_index))
    return ops


def polygon_medial_axis_transform(polygon: Polygon) -> tuple[np.ndarray, np.ndarray]:
    """Compute MAT samples of a polygon.

    Parameters
    ----------
    polygon
        A :class:`compas.geometry.Polygon` lying in the XY plane.

    Returns
    -------
    tuple[numpy.ndarray, numpy.ndarray]
        Interior skeleton points (Mx3) and their clearance radii (M,).
    """
    V = _polygon_to_ccw_vertices(polygon)
    mat_points, mat_radii = _toolpath.polygon_medial_axis_transform(V)
    mat_points = np.asarray(mat_points, dtype=np.float64, order="C")
    mat_radii = np.asarray(mat_radii, dtype=np.float64, order="C").reshape(-1)
    return mat_points, mat_radii


def trochoidal_mat_toolpath(
    polygon: Polygon,
    tool_diameter: float,
    stepover: float | None = None,
    pitch: float | None = None,
    min_trochoid_radius: float = 0.0,
    max_trochoid_radius: float | None = None,
    mat_scale: float = 1.0,
    radial_clearance: float = 1e-4,
    samples_per_cycle: int = 20,
    max_passes: int = 1000,
) -> PolylinesNumpy:
    """Generate adaptive trochoidal pocketing paths from polygon MAT samples.

    Parameters
    ----------
    polygon
        A :class:`compas.geometry.Polygon` lying in the XY plane.
    tool_diameter
        Tool diameter.
    stepover
        Reserved for API compatibility. Defaults to ``0.4 * tool_diameter``.
    pitch
        Trochoid pitch. Defaults to ``0.75 * tool_diameter``.
    min_trochoid_radius
        Minimum desired trochoid radius.
    max_trochoid_radius
        Maximum trochoid radius. Defaults to no cap.
    mat_scale
        Scale factor applied to MAT-derived available radius.
    radial_clearance
        Safety clearance subtracted from MAT availability.
    samples_per_cycle
        Polyline samples per trochoid cycle.
    max_passes
        Maximum number of emitted MAT-edge toolpaths.

    Returns
    -------
    :attr:`compas_cgal.types.PolylinesNumpy`
        List of Nx3 toolpath polylines.
    """
    if stepover is None:
        stepover = 0.4 * tool_diameter
    if pitch is None:
        pitch = 0.75 * tool_diameter
    if max_trochoid_radius is None:
        max_trochoid_radius = float("inf")

    V = _polygon_to_ccw_vertices(polygon)
    paths = _toolpath.trochoidal_mat_toolpath(
        V,
        float(tool_diameter),
        float(stepover),
        float(pitch),
        float(min_trochoid_radius),
        float(max_trochoid_radius),
        float(mat_scale),
        float(radial_clearance),
        int(samples_per_cycle),
        int(max_passes),
    )
    return [np.asarray(path, dtype=np.float64, order="C") for path in paths]


def trochoidal_mat_toolpath_circular(
    polygon: Polygon,
    tool_diameter: float,
    stepover: float | None = None,
    pitch: float | None = None,
    min_trochoid_radius: float = 0.0,
    max_trochoid_radius: float | None = None,
    mat_scale: float = 1.0,
    radial_clearance: float = 1e-4,
    samples_per_cycle: int = 20,
    max_passes: int = 1000,
    lead_in: float = 0.0,
    lead_out: float = 0.0,
    link_paths: bool = True,
    optimize_order: bool = True,
    cut_z: float = 0.0,
    clearance_z: float | None = None,
    retract_at_end: bool = True,
    merge_circles: bool = True,
) -> list[ToolpathOperation]:
    """Generate linked circular arc toolpath operations.

    Parameters
    ----------
    polygon
        A :class:`compas.geometry.Polygon` lying in the XY plane.
    tool_diameter
        Tool diameter.
    stepover
        Reserved for API compatibility. Defaults to ``0.4 * tool_diameter``.
    pitch
        Trochoid pitch. Defaults to ``0.75 * tool_diameter``.
    min_trochoid_radius
        Minimum desired trochoid radius.
    max_trochoid_radius
        Maximum trochoid radius. Defaults to no cap.
    mat_scale
        Scale factor applied to MAT-derived available radius.
    radial_clearance
        Safety clearance subtracted from MAT availability.
    samples_per_cycle
        Polyline samples per trochoid cycle.
    max_passes
        Maximum number of emitted MAT-edge toolpaths.
    lead_in
        Entry line length along the start tangent for each path.
    lead_out
        Exit line length along the end tangent for each path.
    link_paths
        If ``True``, connect consecutive paths with linear link moves.
    optimize_order
        If ``True``, greedily reorder paths by nearest entry.
    cut_z
        Z-height of cutting motions.
    clearance_z
        Safe Z-height for inter-path travel.
    retract_at_end
        If ``True``, add a final retract after the last path.
    merge_circles
        If ``True``, merge consecutive arc pairs forming full circles.

    Returns
    -------
    list[ToolpathOperation]
        Operation stream with typed compas geometry.
    """
    if stepover is None:
        stepover = 0.4 * tool_diameter
    if pitch is None:
        pitch = 0.75 * tool_diameter
    if max_trochoid_radius is None:
        max_trochoid_radius = float("inf")

    has_clearance_z = clearance_z is not None
    effective_clearance_z = float(clearance_z) if clearance_z is not None else 0.0

    V = _polygon_to_ccw_vertices(polygon)
    meta, starts, ends, centers, radii = _toolpath.trochoidal_mat_toolpath_circular(
        V,
        float(tool_diameter),
        float(stepover),
        float(pitch),
        float(min_trochoid_radius),
        float(max_trochoid_radius),
        float(mat_scale),
        float(radial_clearance),
        int(samples_per_cycle),
        int(max_passes),
        float(lead_in),
        float(lead_out),
        bool(link_paths),
        bool(optimize_order),
        float(cut_z),
        effective_clearance_z,
        has_clearance_z,
        bool(retract_at_end),
        bool(merge_circles),
    )

    meta = np.asarray(meta, dtype=np.float64)
    if meta.size == 0:
        return []

    starts = np.asarray(starts, dtype=np.float64, order="C")
    ends = np.asarray(ends, dtype=np.float64, order="C")
    centers = np.asarray(centers, dtype=np.float64, order="C")
    radii = np.asarray(radii, dtype=np.float64, order="C").reshape(-1)

    return _matrices_to_operations(meta, starts, ends, centers, radii)
