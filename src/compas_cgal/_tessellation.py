"""Native array conversion at the CGAL tessellation boundary."""

import numpy as np
from compas.geometry import Tessellation


def validate_boolean_operand(mesh: Tessellation, name: str) -> None:
    """Validate the topology required by CGAL surface-mesh booleans."""
    if not isinstance(mesh, Tessellation):
        raise TypeError(f"{name} should be a Tessellation.")

    incidences: dict[tuple[int, int], list[tuple[int, int]]] = {}
    for triangle in mesh.triangles:
        a, b, c = (int(index) for index in triangle)
        for edge in ((a, b), (b, c), (c, a)):
            key = (min(edge), max(edge))
            incidences.setdefault(key, []).append(edge)

    if any(len(edges) > 2 for edges in incidences.values()):
        raise ValueError(f"{name} should be manifold for a boolean operation.")
    if not incidences or any(len(edges) < 2 for edges in incidences.values()):
        raise ValueError(f"{name} should be closed for a boolean operation.")
    if any(edges[0] != edges[1][::-1] for edges in incidences.values()):
        raise ValueError(f"{name} should be consistently oriented for a boolean operation.")


def as_native_tessellation(mesh: Tessellation) -> tuple[np.ndarray, np.ndarray]:
    """Convert a validated tessellation to the arrays required by CGAL."""
    if not isinstance(mesh, Tessellation):
        raise TypeError("mesh should be a Tessellation.")
    vertices = np.asarray(mesh.vertices, dtype=np.float64, order="C")
    triangles64 = np.asarray(mesh.triangles, dtype=np.int64, order="C")
    info = np.iinfo(np.int32)
    if triangles64.size and (triangles64.min() < info.min or triangles64.max() > info.max):
        raise OverflowError("Triangle indices exceed the range supported by CGAL.")
    return vertices, np.asarray(triangles64, dtype=np.int32, order="C")


def from_native_tessellation(vertices: np.ndarray, triangles: np.ndarray) -> Tessellation:
    """Wrap CGAL output arrays in the canonical triangle representation."""
    return Tessellation(
        np.asarray(vertices, dtype=np.float64, order="C"),  # pyright: ignore[reportArgumentType]
        np.asarray(triangles, dtype=np.int32, order="C"),  # pyright: ignore[reportArgumentType]
    )
