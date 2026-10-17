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
ORIGINAL_MARKER = "# aicommit-original-hook"


def _warn(msg: str) -> None:
    typer.echo(f"aicommit: {msg}", err=True)


def _make_client(cfg: Config):
   
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
    current = hook.read_text() if hook.exists() else ""
    if MARKER in current:
        typer.echo("aicommit hook is already installed.")
        return
    if current and not force:
        typer.echo("A different prepare-commit-msg hook exists. Use --force to chain it.")
        raise typer.Exit(1)
    original = hooks_dir / "prepare-commit-msg.aicommit-original"
    if current:
        if original.exists():
            typer.echo(f"Saved hook already exists: {original}")
            raise typer.Exit(1)
        original.write_text(current)
        original.chmod(hook.stat().st_mode & 0o777)
    # `-I` ignores the repository and user site-packages on Python startup,
    # preventing a repo-local module from shadowing the installed package.
    hook.write_text(
        f'#!/bin/sh\n{MARKER}\n'
        f'"{sys.executable}" -I -m aicommit.cli run "$@" || :\n'
        f'if [ -x "$(dirname "$0")/prepare-commit-msg.aicommit-original" ]; then\n'
        f'  "$(dirname "$0")/prepare-commit-msg.aicommit-original" "$@"\n'
        f'fi\n'
    )
    hook.chmod(0o755)
    typer.echo(f"Installed {hook}")


@app.command()
def uninstall() -> None:
    """Remove the hook, if it is ours."""
    hooks_dir = Path(run_git("rev-parse", "--git-path", "hooks").strip())
    hook = hooks_dir / "prepare-commit-msg"
    if hook.exists() and MARKER in hook.read_text():
        original = hooks_dir / "prepare-commit-msg.aicommit-original"
        if original.exists():
            hook.unlink()
            original.replace(hook)
        else:
            hook.unlink()
        typer.echo("Removed hook.")
    else:
        typer.echo("No aicommit hook found.")


if __name__ == "__main__":
    app()
