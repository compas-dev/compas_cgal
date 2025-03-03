"""COMPAS CGAL is a Python extension that wraps selected functionality of CGAL.

This package provides Python bindings for specific CGAL algorithms and data structures,
focusing on geometry processing and mesh operations.
"""

from .compas_cgal_ext import add, __doc__, scale_matrix, create_matrix
from .compas_cgal_ext.meshing import remesh

__all__ = ["add", "remesh", "scale_matrix", "create_matrix"]
