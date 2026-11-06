from collections.abc import Iterator
from typing import TYPE_CHECKING
from typing import Annotated
from typing import Literal
from typing import Protocol
from typing import Sequence

from compas.typing import Float64Array
from compas.typing import Int32Array
from compas.typing import PointLike
from compas.typing import VectorLike

if TYPE_CHECKING:
    from compas.geometry import Plane


class _SequenceOutput[T](Protocol):
    """Structural sequence returned by Python or native CGAL implementations."""

    def __len__(self) -> int: ...
    def __iter__(self) -> Iterator[T]: ...

    def __getitem__(self, key: int) -> T: ...


type FloatNx3 = Annotated[Float64Array, Literal["N", 3]]
type FloatNx2Or3 = Annotated[Float64Array, Literal["N", "2 or 3"]]
type IntNx3 = Annotated[Int32Array, Literal["N", 3]]
type IntNx2 = Annotated[Int32Array, Literal["N", 2]]
type IntNx4 = Annotated[Int32Array, Literal["N", 4]]

VerticesNumpy = FloatNx3
"""An array of vertices, with each vertex defined by 3 spatial coordinates."""

FacesNumpy = IntNx3
"""An array of faces, with each face defined by 3 vertex indices."""

type VerticesFacesNumpy = tuple[FloatNx3, IntNx3]
"""Representation of a mesh as a tuple of vertices and faces,
with the vertices represented a Nx3 array of spatial coordinates,
and the faces as a Fx3 array of vertex indices.
"""

type DelaunayResult = tuple[list[list[float]], IntNx3]
"""A planar Delaunay result with preserved XYZ coordinates and native triangle indices."""

type VerticesQuadsNumpy = tuple[FloatNx3, IntNx4]
"""Representation of a quad mesh as a tuple of vertex and face arrays."""

type VerticesFacesEdgesNumpy = tuple[FloatNx3, IntNx3, IntNx2]
"""Representation of a boolean result as a tuple of vertices, faces, and
intersection-curve edges, where edges are pairs of vertex indices into V."""

type VerticesFacesSourceNumpy = tuple[FloatNx3, IntNx3, IntNx2]
"""Representation of a boolean result with per-face source tracking. The third
array is Mx2: column 0 is the source mesh id (0 = A, 1 = B), column 1 is the
face index in that source mesh."""

type DualMeshNumpy = tuple[
    FloatNx3,
    IntNx3,
    FloatNx3,
    list[list[int]] | _SequenceOutput[_SequenceOutput[int]],
]
"""Remeshed triangle buffers plus dual vertices and variable-length faces."""

type SkeletonData = tuple[FloatNx3, list[int], IntNx2, list[int]]
"""Raw straight-skeleton vertices, vertex indices, edges, and edge types."""

type PolylinesNumpy = list[FloatNx2Or3] | _SequenceOutput[FloatNx2Or3]
"""A sequence of polylines represented by Nx2 or Nx3 coordinate arrays."""

type PolylinesNumpySkeleton = list[tuple[list[float], list[float]]]
"""A list of polylines, where each polyline is represented by a tuple of start and end point coordinates."""

type SkeletonVertexMapping = list[tuple[list[int], list[int]]]
"""Vertex correspondence mapping for skeleton edges. Each tuple contains two lists:
the first list has indices of original mesh vertices that contracted to the skeleton edge's start vertex,
the second list has indices that contracted to the skeleton edge's end vertex."""

type Planes = Sequence[Plane | tuple[PointLike, VectorLike]]
"""A sequence of planes, with each plane defined as an actual Plane object,
or as a tuple of a point and normal vector, with each point represented by a Point object or an equivalent list of coordinates,
and each vector represented by a Vector object or an equivalent list of components.
"""


__all__ = [
    "DelaunayResult",
    "FacesNumpy",
    "DualMeshNumpy",
    "FloatNx2Or3",
    "FloatNx3",
    "IntNx2",
    "IntNx3",
    "IntNx4",
    "Planes",
    "PolylinesNumpy",
    "PolylinesNumpySkeleton",
    "SkeletonData",
    "SkeletonVertexMapping",
    "VerticesFacesEdgesNumpy",
    "VerticesFacesNumpy",
    "VerticesFacesSourceNumpy",
    "VerticesNumpy",
    "VerticesQuadsNumpy",
]
