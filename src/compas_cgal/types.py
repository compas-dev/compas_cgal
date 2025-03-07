from typing import Annotated
from typing import List
from typing import Literal
from typing import Sequence
from typing import Tuple
from typing import Union

import compas.geometry
from numpy import float64
from numpy import int64
from numpy.typing import NDArray

FloatNx3 = Annotated[NDArray[float64], Literal["N", 3]]
IntNx3 = Annotated[NDArray[int64], Literal["N", 3]]
IntNx2 = Annotated[NDArray[int64], Literal["N", 2]]
IntNx1 = Annotated[NDArray[int64], Literal["N", 1]]

VerticesNumpy = FloatNx3
"""An array of vertices, with each vertex defined by 3 spatial coordinates."""

FacesNumpy = IntNx3
"""An array of faces, with each face defined by 3 vertex indices."""

Vertices = Union[Sequence[Annotated[List[float], 3]], FloatNx3]
"""The vertices of a mesh, defined as an array-like sequence of vertices, with each vertex represented by 3 spatial coordinates."""

Faces = Union[Sequence[Annotated[List[int], 3]], IntNx3]
"""The faces of a mesh, defined as an array-like sequence of faces, with each face represented by 3 vertex indices."""

VerticesFaces = Tuple[Vertices, Faces]
"""Representation of a mesh as a tuple of vertices and faces."""

VerticesFacesNumpy = Tuple[FloatNx3, IntNx3]
"""Representation of a mesh as a tuple of vertices and faces,
with the vertices represented a Nx3 array of spatial coordinates,
and the faces as a Fx3 array of vertex indices.
"""

PolylinesNumpy = List[FloatNx3]
"""A list of polylines, with each polyline represented as a Nx3 array of spatial coordinates."""

PolylinesNumpySkeleton = List[Tuple[List[float], List[float]]]
"""A list of polylines, where each polyline is represented by a tuple of start and end point coordinates."""

Planes = Union[
    Sequence[compas.geometry.Plane],
    Sequence[Tuple[compas.geometry.Point, compas.geometry.Vector]],
    Sequence[Tuple[Annotated[List[float], 3], Annotated[List[float], 3]]],
]
"""A sequence of planes, with each plane defined as an actual Plane object,
or as a tuple of a point and normal vector, with each point represented by a Point object or an equivalent list of coordinates,
and each vector represented by a Vector object or an equivalent list of components.
"""
