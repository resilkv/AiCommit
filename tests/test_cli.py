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
    assert "-I -m aicommit.cli run" in hook.read_text()


def test_force_chains_and_uninstall_restores_existing_hook(tmp_path, monkeypatch):
    subprocess.run(["git", "init", "-q"], cwd=tmp_path, check=True)
    monkeypatch.chdir(tmp_path)
    hook = tmp_path / ".git" / "hooks" / "prepare-commit-msg"
    original = "#!/bin/sh\necho existing-hook \"$@\"\n"
    hook.write_text(original)
    hook.chmod(0o755)

    result = CliRunner().invoke(app, ["install", "--force"])

    assert result.exit_code == 0, result.output
    assert "-I -m aicommit.cli run" in hook.read_text()
    saved = hook.with_name("prepare-commit-msg.aicommit-original")
    assert saved.read_text() == original
    assert "existing-hook" in hook.read_text()

    result = CliRunner().invoke(app, ["uninstall"])
    assert result.exit_code == 0, result.output
    assert hook.read_text() == original
    assert not saved.exists()
