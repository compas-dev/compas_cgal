import os
from importlib.metadata import PackageNotFoundError
from importlib.metadata import version


__author__ = ["tom van mele", "petras vestartas"]
__copyright__ = "Block Research Group - ETH Zurich"
__license__ = "MIT License"
__email__ = ["van.mele@arch.ethz.ch", "vestartas@arch.ethz.ch"]
try:
    __version__ = version("compas_cgal")
except PackageNotFoundError:
    __version__ = "0.0.0"

HERE = os.path.dirname(__file__)

HOME = os.path.abspath(os.path.join(HERE, "../../"))
DATA = os.path.abspath(os.path.join(HOME, "data"))
DOCS = os.path.abspath(os.path.join(HOME, "docs"))
TEMP = os.path.abspath(os.path.join(HOME, "temp"))


__all_plugins__ = [
    "compas_cgal.booleans",
    "compas_cgal.intersections",
    "compas_cgal.isolines",
    "compas_cgal.meshing",
    "compas_cgal.measure",
    "compas_cgal.reconstruction",
    "compas_cgal.triangulation",
    "compas_cgal.slicer",
    "compas_cgal.subdivision",
    "compas_cgal.polylines",
]

__all__ = ["HOME", "DATA", "DOCS", "TEMP"]
