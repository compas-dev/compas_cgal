import os
import subprocess
import sys


def test_installed_plugin_entry_points_are_native_import_free():
    script = """
import importlib.metadata
import sys

expected = {
    "compas_cgal_booleans",
    "compas_cgal_intersections",
    "compas_cgal_mesh",
    "compas_cgal_trimesh",
    "compas_cgal_triangulation",
}
entry_points = {
    entry_point.name: entry_point
    for entry_point in importlib.metadata.entry_points(group="compas.plugins")
    if entry_point.name.startswith("compas_cgal_")
}
assert set(entry_points) == expected
for entry_point in entry_points.values():
    entry_point.load()
assert not [name for name in sys.modules if name.startswith("compas_cgal._")]
"""
    environment = os.environ.copy()
    environment.pop("PYTHONPATH", None)

    subprocess.run([sys.executable, "-c", script], env=environment, check=True)
