from collections.abc import Iterable

import numpy as np
from numpy.typing import NDArray

class VectorDouble(list[float]):
    def __init__(self, value: Iterable[float] = ()) -> None: ...

class VectorInt(list[int]):
    def __init__(self, value: Iterable[int] = ()) -> None: ...

class VectorVectorInt(list[VectorInt]):
    def __init__(self, value: Iterable[Iterable[int]] = ()) -> None: ...

class VectorRowMatrixXd(list[NDArray[np.float64]]):
    def __init__(self, value: Iterable[NDArray[np.float64]] = ()) -> None: ...

class VectorRowMatrixXi(list[NDArray[np.int32]]):
    def __init__(self, value: Iterable[NDArray[np.int32]] = ()) -> None: ...

class VectorVectorRowMatrixXd(list[VectorRowMatrixXd]):
    def __init__(self, value: Iterable[Iterable[NDArray[np.float64]]] = ()) -> None: ...
