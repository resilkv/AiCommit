import subprocess

from typer.testing import CliRunner

from aicommit.cli import MARKER, app


def test_install_creates_prepare_commit_msg_hook(tmp_path, monkeypatch):
    subprocess.run(["git", "init", "-q"], cwd=tmp_path, check=True)
    monkeypatch.chdir(tmp_path)

    result = CliRunner().invoke(app, ["install"])

    hook = tmp_path / ".git" / "hooks" / "prepare-commit-msg"
    assert result.exit_code == 0, result.output
    assert hook.exists()
    assert MARKER in hook.read_text()
    assert "-m aicommit.cli run" in hook.read_text()
