import ast
import subprocess
import sys
import tomllib
from pathlib import Path
from zipfile import ZipFile

import pytest


NATIVE_MODULES = (
    "_booleans",
    "_geodesics",
    "_intersections",
    "_isolines",
    "_measure",
    "_meshing",
    "_polylines",
    "_reconstruction",
    "_skeletonization",
    "_slicer",
    "_straight_skeleton_2",
    "_subdivision",
    "_triangulation",
    "_types_std",
)
COMPAS_CANDIDATE = "3c1a2e8e0e5c4c14292ecf4bb38c82e5b977273e"
VIEWER_CANDIDATE = "cf5a5195bda840a511319d6b7201978af68c15e3"


@pytest.fixture
def verifier() -> Path:
    return Path(__file__).parents[1] / ".github" / "scripts" / "verify_native_wheel.py"


def make_wheel(path: Path, missing_extension: str | None = None, false_extension: str | None = None) -> None:
    with ZipFile(path, "w") as archive:
        archive.writestr("compas_cgal/py.typed", "")
        for module in NATIVE_MODULES:
            archive.writestr(f"compas_cgal/{module}.pyi", "")
            if module != missing_extension:
                archive.writestr(f"compas_cgal/{module}.abi3.so", "native")
        if false_extension:
            archive.writestr(f"compas_cgal/{false_extension}.py", "not native")


def test_complete_typed_native_wheel_is_accepted(tmp_path: Path, verifier: Path) -> None:
    wheel = tmp_path / "compas_cgal.whl"
    make_wheel(wheel)

    result = subprocess.run([sys.executable, verifier, wheel], capture_output=True, text=True)

    assert result.returncode == 0


def test_missing_native_extension_is_rejected(tmp_path: Path, verifier: Path) -> None:
    wheel = tmp_path / "compas_cgal.whl"
    make_wheel(wheel, missing_extension="_triangulation")

    result = subprocess.run([sys.executable, verifier, wheel], capture_output=True, text=True)

    assert result.returncode != 0
    assert "_triangulation" in result.stderr


def test_python_file_does_not_count_as_native_extension(tmp_path: Path, verifier: Path) -> None:
    wheel = tmp_path / "compas_cgal.whl"
    make_wheel(wheel, missing_extension="_triangulation", false_extension="_triangulation")

    result = subprocess.run([sys.executable, verifier, wheel], capture_output=True, text=True)

    assert result.returncode != 0
    assert "_triangulation" in result.stderr


@pytest.mark.parametrize("workflow_name", ["build.yml", "release.yml"])
def test_cibuildwheel_installs_compas_candidate_before_wheel(workflow_name: str) -> None:
    workflow_path = Path(__file__).parents[1] / ".github" / "workflows" / workflow_name
    workflow = workflow_path.read_text(encoding="utf-8")
    before_test, test_requirements = workflow.split("CIBW_BEFORE_TEST:", maxsplit=1)[1].split("CIBW_TEST_REQUIRES:", maxsplit=1)
    test_requirements = test_requirements.splitlines()[0]

    assert COMPAS_CANDIDATE in before_test
    assert "pip install" in before_test
    assert "compas" not in test_requirements.lower()


@pytest.mark.parametrize("workflow_name", ["build.yml", "release.yml"])
def test_workflows_use_supported_intel_macos_runner(workflow_name: str) -> None:
    workflow_path = Path(__file__).parents[1] / ".github" / "workflows" / workflow_name
    workflow = workflow_path.read_text(encoding="utf-8")

    assert "os: macos-15-intel" in workflow
    assert "platform: macos-x86_64" in workflow
    assert "arch: x86_64" in workflow
    assert "macos-13" not in workflow


def test_wheel_smoke_type_checks_the_installed_distribution() -> None:
    workflow_path = Path(__file__).parents[1] / ".github" / "workflows" / "build.yml"
    workflow = workflow_path.read_text(encoding="utf-8")
    wheel_smoke = workflow.split("wheel-smoke:", maxsplit=1)[1].split("sdist:", maxsplit=1)[0]

    assert "Verify installed wheel type contract" in wheel_smoke
    assert "cp tests/typing/*.py" in wheel_smoke
    assert 'python -m pyright --pythonpath "$(command -v python)" .' in wheel_smoke
    assert "python -m pyright --verifytypes compas_cgal --ignoreexternal" in wheel_smoke


def test_installed_wheel_consumers_import_every_wrapper_and_plugin_family() -> None:
    repository = Path(__file__).parents[1]
    consumer_imports = set()
    for consumer_path in (repository / "tests" / "typing").glob("*.py"):
        tree = ast.parse(consumer_path.read_text(encoding="utf-8"))
        consumer_imports.update(node.module for node in tree.body if isinstance(node, ast.ImportFrom) and node.module)

    wrapper_modules = set()
    for module_path in (repository / "src" / "compas_cgal").glob("*.py"):
        if module_path.name.startswith("_") or module_path.name == "types.py":
            continue
        tree = ast.parse(module_path.read_text(encoding="utf-8"))
        if any(
            isinstance(node, ast.Assign)
            and isinstance(node.value, (ast.List, ast.Tuple))
            and bool(node.value.elts)
            and any(isinstance(target, ast.Name) and target.id == "__all__" for target in node.targets)
            for node in tree.body
        ):
            wrapper_modules.add(f"compas_cgal.{module_path.stem}")

    plugin_modules = {
        f"compas_cgal.plugins.{module_path.stem}" for module_path in (repository / "src" / "compas_cgal" / "plugins").glob("*.py") if module_path.name != "__init__.py"
    }

    assert wrapper_modules <= consumer_imports
    assert plugin_modules <= consumer_imports


def test_quality_gates_include_executable_documentation_examples() -> None:
    repository = Path(__file__).parents[1]
    pyproject = tomllib.loads((repository / "pyproject.toml").read_text(encoding="utf-8"))
    workflow = (repository / ".github" / "workflows" / "build.yml").read_text(encoding="utf-8")

    assert "docs/examples" in pyproject["tool"]["pyright"]["include"]
    assert "uv run pyright" in workflow
    assert "uv run ruff check ." in workflow


def test_visualization_extra_uses_exact_viewer_candidate() -> None:
    repository = Path(__file__).parents[1]
    pyproject = tomllib.loads((repository / "pyproject.toml").read_text(encoding="utf-8"))
    source = pyproject["tool"]["uv"]["sources"]["compas-viewer"]

    assert source == {
        "git": "https://github.com/compas-dev/compas_viewer.git",
        "rev": VIEWER_CANDIDATE,
    }


def test_candidate_workflows_trigger_for_c3_upgrade() -> None:
    repository = Path(__file__).parents[1]

    for workflow_name in ("build.yml", "docs.yml", "pr-checks.yml"):
        workflow = (repository / ".github" / "workflows" / workflow_name).read_text(encoding="utf-8")
        pull_request_trigger = workflow.split("pull_request:", maxsplit=1)[1].splitlines()[1]
        assert "c3-upgrade" in pull_request_trigger

    build = (repository / ".github" / "workflows" / "build.yml").read_text(encoding="utf-8")
    push_trigger = build.split("push:", maxsplit=1)[1].splitlines()[1]
    assert "c3-upgrade" in push_trigger


def test_numpy_compatibility_gate_covers_lowest_and_current_runtime_and_typing() -> None:
    repository = Path(__file__).parents[1]
    pyproject = tomllib.loads((repository / "pyproject.toml").read_text(encoding="utf-8"))
    workflow = (repository / ".github" / "workflows" / "build.yml").read_text(encoding="utf-8")
    compatibility = workflow.split("numpy-compatibility:", maxsplit=1)[1].split("wheels:", maxsplit=1)[0]

    assert "numpy>=1.26" in pyproject["project"]["dependencies"]
    assert 'numpy: "numpy==1.26.*"' in compatibility
    assert 'numpy: "numpy"' in compatibility
    assert workflow.count("dependency-groups: dev,viz") == 2
    assert workflow.count('extras: ""') == 2
    assert "uv run --no-sync pytest" in compatibility
    assert "uv run --no-sync pyright" in compatibility
    assert "PYTHONPATH=src uv run --no-sync pyright --verifytypes compas_cgal --ignoreexternal" in compatibility


def test_distribution_uses_pep639_lgpl_metadata() -> None:
    repository = Path(__file__).parents[1]
    pyproject = tomllib.loads((repository / "pyproject.toml").read_text(encoding="utf-8"))

    assert pyproject["project"]["license"] == "LGPL-3.0-only"
    assert pyproject["project"]["license-files"] == ["LICENSE"]
    assert not [classifier for classifier in pyproject["project"]["classifiers"] if classifier.startswith("License ::")]
    assert (repository / "LICENSE").is_file()

    package_tree = ast.parse((repository / "src" / "compas_cgal" / "__init__.py").read_text(encoding="utf-8"))
    license_assignment = next(
        node for node in package_tree.body if isinstance(node, ast.Assign) and any(isinstance(target, ast.Name) and target.id == "__license__" for target in node.targets)
    )
    assert isinstance(license_assignment.value, ast.Constant)
    assert license_assignment.value.value == "LGPL-3.0-only"


def test_distribution_declares_only_plugin_modules_with_core_extension_points() -> None:
    repository = Path(__file__).parents[1]
    pyproject = tomllib.loads((repository / "pyproject.toml").read_text(encoding="utf-8"))

    assert pyproject["project"]["entry-points"]["compas.plugins"] == {
        "compas_cgal_booleans": "compas_cgal.plugins.booleans",
        "compas_cgal_intersections": "compas_cgal.plugins.intersections",
        "compas_cgal_trimesh": "compas_cgal.plugins.trimesh",
        "compas_cgal_triangulation": "compas_cgal.plugins.triangulation",
    }
    assert not (repository / "src" / "compas_cgal" / "plugins" / "mesh.py").exists()


def test_weighted_straight_skeleton_calls_match_cgal_6_1_1_api() -> None:
    repository = Path(__file__).parents[1]
    source = (repository / "src" / "straight_skeleton_2.cpp").read_text(encoding="utf-8")
    compact = "".join(source.split())

    assert "std::vector<std::vector<double>>weights={weight_values};" in compact
    assert "create_interior_weighted_straight_skeleton_2(polygon,weights)" in compact
    assert "create_exterior_weighted_straight_skeleton_2(offset_distance,polygon,weights)" in compact
    assert "create_interior_weighted_straight_skeleton_2(polygon,weight_values)" not in compact
    assert "create_exterior_weighted_straight_skeleton_2(offset_distance,polygon,weight_values)" not in compact
