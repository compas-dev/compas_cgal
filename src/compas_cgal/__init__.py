from __future__ import print_function

import os


__author__ = ["tom van mele"]
__copyright__ = "Block Research Group - ETH Zurich"
__license__ = "MIT License"
__email__ = "van.mele@arch.ethz.ch"
__version__ = "0.5.0"

HERE = os.path.dirname(__file__)

HOME = os.path.abspath(os.path.join(HERE, "../../"))
DATA = os.path.abspath(os.path.join(HOME, "data"))
DOCS = os.path.abspath(os.path.join(HOME, "docs"))
TEMP = os.path.abspath(os.path.join(HOME, "temp"))


__all_plugins__ = [
    "compas_cgal.booleans",
    "compas_cgal.intersections",
    "compas_cgal.meshing",
    "compas_cgal.measure",
    "compas_cgal.slicer",
    "compas_cgal.triangulation",
]

__all__ = ["HOME", "DATA", "DOCS", "TEMP"]
