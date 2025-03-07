import os


__author__ = ["tom van mele", "petras vestartas"]
__copyright__ = "Block Research Group - ETH Zurich"
__license__ = "MIT License"
__email__ = ["van.mele@arch.ethz.ch", "vestartas@arch.ethz.ch"]
__version__ = "1.0.1"

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
    "compas_cgal.reconstruction",
    "compas_cgal.triangulation",
    "compas_cgal.slicer",
    "compas_cgal.subdivision",
]

__all__ = ["HOME", "DATA", "DOCS", "TEMP"]
