from typing import Tuple
from typing import List
from typing import Union
from typing import Sequence
from typing_extensions import Annotated
from nptyping import NDArray, Shape

import compas.geometry
import numpy as np

SequenceOfVertices = Union[
    Sequence[Annotated[List[float], 3]],
    NDArray[Shape["*, 3"], np.float64],  # noqa: F722
]

SequenceOfFaces = Union[
    Sequence[Annotated[List[int], 3]],
    NDArray[Shape["*, 3"], np.int32],  # noqa: F722
]

VerticesFacesNumpy = Tuple[
    NDArray[Shape["*, 3"], np.float64], NDArray[Shape["*, 3"], np.int32]  # noqa: F722
]

VerticesFaces = Union[
    VerticesFacesNumpy,
    Tuple[List[Annotated[List[float], 3]], List[Annotated[List[int], 3]]],  # noqa: F722
]

ListOfPolylinesNumpy = List[NDArray[Shape["*, 3"], np.float64]]  # noqa: F722

ListOfPlanes = List[
    Union[
        compas.geometry.Plane,
        Tuple[compas.geometry.Point, compas.geometry.Vector],
        Tuple[Annotated[List[float], 3], Annotated[List[float], 3]],
    ]
]
