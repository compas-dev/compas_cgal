import subprocess
import sys
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
COMPAS_CANDIDATE = "e54f8ae0eba39e84b1290bea9c368a1a646dfdcd"


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
