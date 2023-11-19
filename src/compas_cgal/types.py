from __future__ import annotations
from typing import Any
from typing import Tuple
from typing import List
from typing import Union
from typing import Sequence
from typing_extensions import Annotated
from nptyping import NDArray
from nptyping import Shape
from nptyping import Int
from nptyping import Float

import compas.geometry


VerticesNumpy = NDArray[Shape["Any, 3"], Float]
"""An array of vertices, with each vertex defined by 3 spatial coordinates."""

FacesNumpy = NDArray[Shape["Any, 3"], Int]
"""An array of faces, with each face defined by 3 vertex indices."""

Vertices = Union[
    Sequence[Annotated[List[float], 3]],
    NDArray[Shape["Any, 3"], Float],
]
"""The vertices of a mesh, defined as an array-like sequence of vertices, with each vertex represented by 3 spatial coordinates."""

Faces = Union[
    Sequence[Annotated[List[int], 3]],
    NDArray[Shape["Any, 3"], Int],
]
"""The faces of a mesh, defined as an array-like sequence of faces, with each face represented by 3 vertex indices."""

VerticesFaces = Tuple[
    Vertices,
    Faces,
]
"""Representation of a mesh as a tuple of vertices and faces."""

VerticesFacesNumpy = Tuple[
    NDArray[Shape["Any, 3"], Float],
    NDArray[Shape["Any, 3"], Int],
]
"""Representation of a mesh as a tuple of vertices and faces,
with the vertices represented a Nx3 array of spatial coordinates,
and the faces as a Fx3 array of vertex indices.
"""

PolylinesNumpy = List[NDArray[Shape["Any, 3"], Float]]
"""A list of polylines, with each polyline represented as a Nx3 array of spatial coordinates."""

Planes = Union[
    Sequence[compas.geometry.Plane],
    Sequence[Tuple[compas.geometry.Point, compas.geometry.Vector]],
    Sequence[Tuple[Annotated[List[float], 3], Annotated[List[float], 3]]],
]
"""A sequence of planes, with each plane defined as an actual Plane object,
or as a tuple of a point and normal vector, with each point represented by a Point object or an equivalent list of coordinates,
and each vector represented by a Vector object or an equivalent list of components.
"""
