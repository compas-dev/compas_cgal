from __future__ import annotations

from typing import Any
from typing import Dict
from typing import Optional
from typing import List
from typing import Tuple
from nptyping import NDArray

import numpy as np
import scipy as sp
from compas.geometry import Transformation
from compas.datastructures import Mesh


class TriMesh:

    def __init__(self, vertices, faces) -> TriMesh:
        pass

    def __iter__(self):
        pass

    def __getitem__(self, key):
        pass

    def __setitem__(self, key, value):
        pass

    @property
    def vertices(self) -> NDArray[(Any, 3), np.float64]:
        pass

    @vertices.setter
    def vertices(self, vertices):
        pass

    @property
    def faces(self) -> NDArray[(Any, 3), np.int32]:
        pass

    @faces.setter
    def faces(self, faces):
        pass

    @property
    def adjacency(self) -> Dict[int, List[int]]:
        pass

    @property
    def edges(self) -> List[Tuple[int, int]]:
        pass

    @property
    def C(self) -> sp.sparse.csr_matrix:
        pass

    @property
    def A(self) -> sp.sparse.csr_matrix:
        pass

    @property
    def D(self) -> sp.sparse.csr_matrix:
        pass

    @property
    def centroid(self):
        pass

    @property
    def average_edge_length(self) -> float:
        pass

    @classmethod
    def from_stl(cls: TriMesh, filepath: str, precision: Optional[str] = None) -> TriMesh:
        pass

    @classmethod
    def from_ply(cls: TriMesh, filepath: str, precision: Optional[str] = None) -> TriMesh:
        pass

    @classmethod
    def from_off(cls: TriMesh, filepath: str, precision: Optional[str] = None) -> TriMesh:
        pass

    @classmethod
    def from_mesh(cls: TriMesh, mesh: Mesh) -> TriMesh:
        pass

    def to_mesh(self) -> Mesh:
        pass

    def copy(self) -> TriMesh:
        pass

    def transform(self, T: Transformation):
        pass

    def transformed(self, T: Transformation) -> TriMesh:
        pass

    def cull_vertices(self):
        pass

    def remesh(self, target_length: float, iterations: int = 10):
        pass
