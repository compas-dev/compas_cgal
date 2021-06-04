import numpy as np
from compas.geometry import transform_points_numpy
from compas.files import STL
from compas.files import OFF
from compas.files import PLY
from compas.datastructures import Mesh
from compas.numerical import connectivity_matrix
from compas.numerical import adjacency_matrix
from compas.numerical import degree_matrix
from compas.numerical import normrow

from compas_cgal.meshing import remesh


__all__ = ['TriMesh']


class TriMesh(object):

    def __init__(self, vertices, faces):
        self._vertices = None
        self._faces = None
        self._adjacency = None
        self._edges = None
        self.vertices = vertices
        self.faces = faces

    def __iter__(self):
        yield self.vertices
        yield self.faces

    def __getitem__(self, key):
        if key == 0:
            return self.vertices
        if key == 1:
            return self.faces
        raise KeyError

    def __setitem__(self, key, value):
        if key == 0:
            self.vertices = value
        elif key == 1:
            self.faces = value
        else:
            raise KeyError

    @property
    def vertices(self):
        return self._vertices

    @vertices.setter
    def vertices(self, vertices):
        self._adjacency = None
        self._edges = None
        self._vertices = np.asarray(vertices, dtype=np.float64)

    @property
    def faces(self):
        return self._faces

    @faces.setter
    def faces(self, faces):
        self._adjacency = None
        self._edges = None
        self._faces = np.asarray(faces, dtype=np.int32)

    @property
    def adjacency(self):
        if not self._adjacency:
            adj = {i: [] for i in range(self.vertices.shape[0])}
            for a, b, c in self.faces:
                if b not in adj[a]:
                    adj[a].append(b)
                if c not in adj[a]:
                    adj[a].append(c)
                if a not in adj[b]:
                    adj[b].append(a)
                if c not in adj[b]:
                    adj[b].append(c)
                if a not in adj[c]:
                    adj[c].append(a)
                if b not in adj[c]:
                    adj[c].append(b)
            self._adjacency = adj
        return self._adjacency

    @property
    def edges(self):
        if not self._edges:
            seen = set()
            edges = []
            for i, nbrs in self.adjacency.items():
                for j in nbrs:
                    if (i, j) in seen:
                        continue
                    seen.add((i, j))
                    seen.add((i, j))
                    edges.append((i, j))
            self._edges = edges
        return self._edges

    @property
    def C(self):
        return connectivity_matrix(self.edges, 'csr')

    @property
    def A(self):
        return adjacency_matrix(self.adjacency, 'csr')

    @property
    def D(self):
        return degree_matrix(self.adjacency, 'csr')

    @property
    def centroid(self):
        return np.mean(self.vertices, axis=0)

    @property
    def average_edge_length(self):
        return np.mean(normrow(self.C.dot(self.vertices)), axis=0)

    @classmethod
    def from_stl(cls, filepath, precision=None):
        stl = STL(filepath, precision)
        return cls(stl.parser.vertices, stl.parser.faces)

    @classmethod
    def from_ply(cls, filepath, precision=None):
        ply = PLY(filepath, precision)
        return cls(ply.parser.vertices, ply.parser.faces)

    @classmethod
    def from_off(cls, filepath, precision=None):
        off = OFF(filepath, precision)
        return cls(off.reader.vertices, off.reader.faces)

    @classmethod
    def from_mesh(cls, mesh):
        V, F = mesh.to_vertices_and_faces()
        return cls(V, F)

    def to_mesh(self):
        return Mesh.from_vertices_and_faces(self.vertices, self.faces)

    def copy(self):
        cls = type(self)
        return cls(self.vertices.copy(), self.faces.copy())

    def transform(self, T):
        self.vertices[:] = transform_points_numpy(self.vertices, T)

    def transformed(self, T):
        mesh = self.copy()
        mesh.transform(T)
        return mesh

    def cull_vertices(self):
        indices = np.unique(self.faces)
        indexmap = {index: i for i, index in enumerate(indices)}
        self.vertices = self.vertices[indices]
        for face in self.faces:
            face[0] = indexmap[face[0]]
            face[1] = indexmap[face[1]]
            face[2] = indexmap[face[2]]

    def remesh(self, target_length, iterations=10):
        V, F = remesh(self, target_length, iterations)
        self.vertices = V
        self.faces = F
