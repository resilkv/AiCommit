import subprocess
from aicommit.git import staged_diff


def _init_repo(path):
    for cmd in (["git", "init"],
                ["git", "config", "user.email", "t@t.dev"],
                ["git", "config", "user.name", "tester"]):
        subprocess.run(cmd, cwd=path, check=True, capture_output=True)


def _stage_all(path):
    subprocess.run(["git", "add", "."], cwd=path, check=True)


def test_ignored_files_removed(tmp_path):
    _init_repo(tmp_path)
    (tmp_path / "app.py").write_text("print('hi')\n")
    (tmp_path / "uv.lock").write_text("lockdata\n")
    _stage_all(tmp_path)
    diff = staged_diff(cwd=tmp_path)
    assert "app.py" in diff
    assert "uv.lock" not in diff


def test_truncates_large_diff(tmp_path):
    _init_repo(tmp_path)
    (tmp_path / "big.py").write_text("x = 1\n" * 5000)
    _stage_all(tmp_path)
    diff = staged_diff(max_chars=500, cwd=tmp_path)
    assert diff.endswith("[diff truncated]\n")