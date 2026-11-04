from typing import TYPE_CHECKING
from typing import Annotated
from typing import Literal
from typing import Sequence

from compas._typing import CoordinatesInput
from compas._typing import Float64Array
from compas._typing import IndicesCollectionInput
from compas._typing import Int32Array

if TYPE_CHECKING:
    from compas.geometry import Plane
    from compas.geometry import Point
    from compas.geometry import Vector

type FloatNx3 = Annotated[Float64Array, Literal["N", 3]]
type IntNx3 = Annotated[Int32Array, Literal["N", 3]]
type IntNx2 = Annotated[Int32Array, Literal["N", 2]]
type IntNx1 = Annotated[Int32Array, Literal["N", 1]]

VerticesNumpy = FloatNx3
"""An array of vertices, with each vertex defined by 3 spatial coordinates."""

FacesNumpy = IntNx3
"""An array of faces, with each face defined by 3 vertex indices."""

type Vertices = CoordinatesInput
"""Public vertex input accepted as coordinate sequences or numeric arrays.

This public vocabulary is distinct from :attr:`VerticesNumpy`, which describes
the representation required after normalization at a native boundary.
"""

type Faces = IndicesCollectionInput
"""Public face input accepted as index sequences or integer arrays.

This public vocabulary is distinct from :attr:`FacesNumpy`, which describes
the representation required after normalization at a native boundary.
"""

type VerticesFaces = tuple[Vertices, Faces]
"""Representation of a mesh as a tuple of vertices and faces."""

type VerticesFacesNumpy = tuple[FloatNx3, IntNx3]
"""Representation of a mesh as a tuple of vertices and faces,
with the vertices represented a Nx3 array of spatial coordinates,
and the faces as a Fx3 array of vertex indices.
"""

type VerticesFacesEdgesNumpy = tuple[FloatNx3, IntNx3, IntNx2]
"""Representation of a boolean result as a tuple of vertices, faces, and
intersection-curve edges, where edges are pairs of vertex indices into V."""

type VerticesFacesSourceNumpy = tuple[FloatNx3, IntNx3, IntNx2]
"""Representation of a boolean result with per-face source tracking. The third
array is Mx2: column 0 is the source mesh id (0 = A, 1 = B), column 1 is the
face index in that source mesh."""

type PolylinesNumpy = list[FloatNx3]
"""A list of polylines, with each polyline represented as a Nx3 array of spatial coordinates."""

type PolylinesNumpySkeleton = list[tuple[list[float], list[float]]]
"""A list of polylines, where each polyline is represented by a tuple of start and end point coordinates."""

type SkeletonVertexMapping = list[tuple[list[int], list[int]]]
"""Vertex correspondence mapping for skeleton edges. Each tuple contains two lists:
the first list has indices of original mesh vertices that contracted to the skeleton edge's start vertex,
the second list has indices that contracted to the skeleton edge's end vertex."""

type Planes = Sequence[Plane] | Sequence[tuple[Point, Vector]] | Sequence[tuple[Sequence[float], Sequence[float]]]
"""A sequence of planes, with each plane defined as an actual Plane object,
or as a tuple of a point and normal vector, with each point represented by a Point object or an equivalent list of coordinates,
and each vector represented by a Vector object or an equivalent list of components.
"""
