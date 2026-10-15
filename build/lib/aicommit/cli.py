import os
import sys
from pathlib import Path
from typing import Optional

import typer
from dotenv import load_dotenv

from .config import Config, load_config
from .git import run_git, staged_diff
from .pipeline import generate_message

app = typer.Typer(add_completion=False, help="AI-written commit messages.")
MARKER = "# aicommit-hook"


def _warn(msg: str) -> None:
    typer.echo(f"aicommit: {msg}", err=True)


def _make_client(cfg: Config):
    if os.environ.get("AICOMMIT_PROVIDER") == "fake":
        from .llm.fake import FakeLLM
        return FakeLLM()
    from .llm.bedrock import BedrockClient
    return BedrockClient(cfg.model_id, cfg.region, cfg.max_tokens)


@app.command()
def run(
    msg_file: Path,
    source: Optional[str] = typer.Argument(None),
    sha: Optional[str] = typer.Argument(None),
) -> None:
    """Called by the git hook. Pre-fills the commit message file."""
    if source is not None:      # -m, merge, squash, amend, template: leave it alone
        return
    try:                        # fail open: never block a commit
        load_dotenv()
        cfg = load_config()
        diff = staged_diff(cfg.ignore, cfg.max_diff_chars)
        if not diff.strip():
            return
        _warn("writing commit message...")
        msg = generate_message(_make_client(cfg), diff)
        existing = msg_file.read_text()
        msg_file.write_text(msg.render() + "\n" + existing)
    except Exception as e:
        _warn(f"skipped ({type(e).__name__}: {e})")


@app.command()
def install(force: bool = typer.Option(False, "--force")) -> None:
    """Install the prepare-commit-msg hook in this repo."""
    hooks_dir = Path(run_git("rev-parse", "--git-path", "hooks").strip())
    hooks_dir.mkdir(parents=True, exist_ok=True)
    hook = hooks_dir / "prepare-commit-msg"
    if hook.exists() and MARKER not in hook.read_text() and not force:
        typer.echo("A different prepare-commit-msg hook exists. Use --force to overwrite.")
        raise typer.Exit(1)
    hook.write_text(f'#!/bin/sh\n{MARKER}\n"{sys.executable}" -m aicommit.cli run "$@" || exit 0\n')
    hook.chmod(0o755)
    typer.echo(f"Installed {hook}")


@app.command()
def uninstall() -> None:
    """Remove the hook, if it is ours."""
    hooks_dir = Path(run_git("rev-parse", "--git-path", "hooks").strip())
    hook = hooks_dir / "prepare-commit-msg"
    if hook.exists() and MARKER in hook.read_text():
        hook.unlink()
        typer.echo("Removed hook.")
    else:
        typer.echo("No aicommit hook found.")


if __name__ == "__main__":
    app()