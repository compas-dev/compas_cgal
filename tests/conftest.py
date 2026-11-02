from pathlib import Path

import pytest


@pytest.fixture(autouse=True)
def isolated_working_directory(tmp_path: Path, monkeypatch: pytest.MonkeyPatch):
    """Run every test from an isolated temporary working directory.

    Native code may write diagnostic files using relative paths. Keeping the
    process working directory outside the source tree prevents those files from
    overwriting or polluting the repository root.

    """
    monkeypatch.chdir(tmp_path)
    yield
