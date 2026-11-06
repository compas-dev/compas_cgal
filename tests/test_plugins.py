from importlib.metadata import EntryPoint
import os
import subprocess
import sys

from compas.plugins import ExtensionPoint
from compas.plugins import PluginManager


def _source_entry_points():
    return [
        EntryPoint(name="compas_cgal_booleans", value="compas_cgal.plugins.booleans", group="compas.plugins"),
        EntryPoint(name="compas_cgal_intersections", value="compas_cgal.plugins.intersections", group="compas.plugins"),
        EntryPoint(name="compas_cgal_trimesh", value="compas_cgal.plugins.trimesh", group="compas.plugins"),
        EntryPoint(name="compas_cgal_triangulation", value="compas_cgal.plugins.triangulation", group="compas.plugins"),
    ]


def test_plugin_registration_matches_current_core_extension_points():
    manager = PluginManager(entry_points_provider=lambda *, group: _source_entry_points())

    assert manager.load_plugins() == 9
    assert set(manager.registry) == {
        ExtensionPoint(domain="https://plugins.compas.dev/", category="booleans", name="_boolean_union_mesh_mesh"),
        ExtensionPoint(domain="https://plugins.compas.dev/", category="booleans", name="_boolean_difference_mesh_mesh"),
        ExtensionPoint(domain="https://plugins.compas.dev/", category="booleans", name="_boolean_intersection_mesh_mesh"),
        ExtensionPoint(domain="https://plugins.compas.dev/", category="intersections", name="_intersection_mesh_mesh"),
        ExtensionPoint(domain="https://plugins.compas.dev/", category="trimesh", name="_trimesh_remesh"),
        ExtensionPoint(domain="https://plugins.compas.dev/", category="trimesh", name="_trimesh_slice"),
        ExtensionPoint(domain="https://plugins.compas.dev/", category="triangulation", name="_delaunay_triangulation"),
        ExtensionPoint(domain="https://plugins.compas.dev/", category="triangulation", name="_constrained_delaunay_triangulation"),
        ExtensionPoint(domain="https://plugins.compas.dev/", category="triangulation", name="_conforming_delaunay_triangulation"),
    }
    assert {plugin.plugin.__name__ for implementations in manager.registry.values() for plugin in implementations} == {
        "compas_cgal.plugins.booleans",
        "compas_cgal.plugins.intersections",
        "compas_cgal.plugins.triangulation",
        "compas_cgal.plugins.trimesh",
    }


def test_missing_native_extension_prevents_selection(monkeypatch):
    manager = PluginManager(entry_points_provider=lambda *, group: _source_entry_points())
    assert manager.load_plugins() == 9
    extension_point = ExtensionPoint(
        domain="https://plugins.compas.dev/",
        category="booleans",
        name="_boolean_union_mesh_mesh",
    )
    plugin = manager.registry[extension_point][0]

    assert plugin.spec.requires == ("compas_cgal._booleans",)
    monkeypatch.setattr(manager, "verify_requirement", lambda requirement: requirement != "compas_cgal._booleans")
    assert manager.select(extension_point) is None


def test_each_plugin_declares_its_actual_compiled_module_requirement():
    manager = PluginManager(entry_points_provider=lambda *, group: _source_entry_points())
    assert manager.load_plugins() == 9
    expected = {
        ("booleans", "_boolean_union_mesh_mesh"): ("compas_cgal._booleans",),
        ("booleans", "_boolean_difference_mesh_mesh"): ("compas_cgal._booleans",),
        ("booleans", "_boolean_intersection_mesh_mesh"): ("compas_cgal._booleans",),
        ("intersections", "_intersection_mesh_mesh"): ("compas_cgal._intersections",),
        ("trimesh", "_trimesh_remesh"): ("compas_cgal._meshing",),
        ("trimesh", "_trimesh_slice"): ("compas_cgal._slicer",),
        ("triangulation", "_delaunay_triangulation"): ("compas_cgal._triangulation",),
        ("triangulation", "_constrained_delaunay_triangulation"): ("compas_cgal._triangulation",),
        ("triangulation", "_conforming_delaunay_triangulation"): ("compas_cgal._triangulation",),
    }

    actual = {(point.category, point.name): implementations[0].spec.requires for point, implementations in manager.registry.items()}

    assert actual == expected


def test_installed_plugin_entry_points_are_native_import_free():
    script = """
import importlib.metadata
import sys

expected = {
    "compas_cgal_booleans",
    "compas_cgal_intersections",
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
