from __future__ import annotations

from typing import Any
from typing import Tuple
from typing import List
from typing import Union
from typing_extensions import Annotated
from nptyping import NDArray

import compas.geometry
import numpy as np

VerticesFacesNumpy = Tuple[
    NDArray[(Any, 3), np.float64],
    NDArray[(Any, 3), np.int32]
]

VerticesFaces = Union[
    VerticesFacesNumpy,
    Tuple[
        List[Annotated[List[float], 3]],
        List[Annotated[List[int], 3]]
    ]
]

ListOfPolylinesNumpy = List[NDArray[(Any, 3), np.float64]]

ListOfPlanes = List[
    Union[
        compas.geometry.Plane,
        Tuple[
            compas.geometry.Point,
            compas.geometry.Vector
        ],
        Tuple[
            Annotated[List[float], 3],
            Annotated[List[float], 3]
        ]
    ]
]
