from pathlib import Path


def test_working_directory_is_isolated(tmp_path: Path):
    repository_root = Path(__file__).parents[1].resolve()

    assert Path.cwd() == tmp_path
    assert Path.cwd() != repository_root

    Path("input_A.off").touch()
    Path("input_B.off").touch()
    Path("output.off").touch()

    assert (tmp_path / "input_A.off").is_file()
    assert (tmp_path / "input_B.off").is_file()
    assert (tmp_path / "output.off").is_file()
