"""
********************************************************************************
compas_cgal
********************************************************************************

.. currentmodule:: compas_cgal

Classes
=======

.. autosummary::
    :toctree: generated/
    :nosignatures:

    trimesh.TriMesh

Functions
=========

Booleans
--------

.. autosummary::
    :toctree: generated/
    :nosignatures:

    booleans.boolean_union
    booleans.boolean_difference
    booleans.boolean_intersection

Intersections
-------------

.. autosummary::
    :toctree: generated/
    :nosignatures:

    intersections.intersection_mesh_mesh

Measure
-------

.. autosummary::
    :toctree: generated/
    :nosignatures:

    measure.volume

Meshing
-------

.. autosummary::
    :toctree: generated/
    :nosignatures:

    meshing.remesh

Slicer
------

.. autosummary::
    :toctree: generated/
    :nosignatures:

    slicer.slice_mesh

Slicer
------

.. autosummary::
    :toctree: generated/
    :nosignatures:

    triangulation.constrained_delaunay_triangulation

"""
from __future__ import print_function

import os


__author__ = ["tom van mele"]
__copyright__ = "Block Research Group - ETH Zurich"
__license__ = "MIT License"
__email__ = "van.mele@arch.ethz.ch"
__version__ = "0.3.0rc0"

HERE = os.path.dirname(__file__)

HOME = os.path.abspath(os.path.join(HERE, "../../"))
DATA = os.path.abspath(os.path.join(HOME, "data"))
DOCS = os.path.abspath(os.path.join(HOME, "docs"))
TEMP = os.path.abspath(os.path.join(HOME, "temp"))


__all_plugins__ = [
    'compas_cgal.booleans',
    'compas_cgal.intersections',
    'compas_cgal.meshing',
    'compas_cgal.slicer',
]

__all__ = ["HOME", "DATA", "DOCS", "TEMP"]
