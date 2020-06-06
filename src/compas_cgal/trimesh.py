from __future__ import print_function
from __future__ import absolute_import
from __future__ import division

import numpy as np


__all__ = []


class TriMesh(object):

    def __init__(self, vertices, faces):
        self.vertices = np.asarray(vertices, dtype=np.float64)
        self.faces = np.asarray(faces, dtype=np.int)
