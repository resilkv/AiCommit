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


def test_ignored_quoted_secret_path_removed(tmp_path):
    _init_repo(tmp_path)
    secret = tmp_path / 'secret "credentials".env'
    secret.write_text("AWS_SECRET_ACCESS_KEY=do-not-send\n")
    (tmp_path / "safe.py").write_text("print('safe')\n")
    _stage_all(tmp_path)

    diff = staged_diff(cwd=tmp_path)

    assert "safe.py" in diff
    assert "do-not-send" not in diff


def test_ignored_env_directory_file_removed(tmp_path):
    _init_repo(tmp_path)
    env_dir = tmp_path / "config"
    env_dir.mkdir()
    (env_dir / ".env.production").write_text("TOKEN=do-not-send\n")
    _stage_all(tmp_path)

    assert "do-not-send" not in staged_diff(cwd=tmp_path)
