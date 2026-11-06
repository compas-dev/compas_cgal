"""Static coverage of accepted inputs at native extension boundaries."""

import numpy as np

from compas_cgal import _meshing
from compas_cgal._types_std import VectorInt


vertices = np.asarray([[0.0, 0.0, 0.0], [1.0, 0.0, 0.0], [0.0, 1.0, 0.0]], dtype=np.float64)
faces = np.asarray([[0, 1, 2]], dtype=np.int32)

_meshing.pmp_trimesh_remesh_dual(vertices, faces, [0, 2])
_meshing.pmp_trimesh_remesh_dual(vertices, faces, (0, 2))
_meshing.pmp_trimesh_remesh_dual(vertices, faces, range(0, 3, 2))
_meshing.pmp_trimesh_remesh_dual(vertices, faces, [np.int32(0), np.int64(2)])
_meshing.pmp_trimesh_remesh_dual(vertices, faces, np.asarray([0, 2], dtype=np.int8))
_meshing.pmp_trimesh_remesh_dual(vertices, faces, np.asarray([0, 2], dtype=np.int16))
_meshing.pmp_trimesh_remesh_dual(vertices, faces, np.asarray([0, 2], dtype=np.int32))
_meshing.pmp_trimesh_remesh_dual(vertices, faces, np.asarray([0, 2], dtype=np.int64))
_meshing.pmp_trimesh_remesh_dual(vertices, faces, np.asarray([0, 2], dtype=np.uint8))
_meshing.pmp_trimesh_remesh_dual(vertices, faces, np.asarray([0, 2], dtype=np.uint32))
_meshing.pmp_trimesh_remesh_dual(vertices, faces, np.asarray([0, 2], dtype=np.uint64))
_meshing.pmp_trimesh_remesh_dual(vertices, faces, VectorInt([0, 2]))
