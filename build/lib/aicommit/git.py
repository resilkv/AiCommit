import re
import subprocess
from fnmatch import fnmatch

DEFAULT_IGNORE = [
    "*.lock", "package-lock.json", "yarn.lock", "pnpm-lock.yaml",
    "*.min.js", "*.map", ".env", ".env.*",
    "*.png", "*.jpg", "*.jpeg", "*.gif", "*.pdf", "*.zip",
]


def run_git(*args: str, cwd=None) -> str:
    result = subprocess.run(
        ["git", *args], capture_output=True, text=True, check=True, cwd=cwd
    )
    return result.stdout


def _path_from_chunk(chunk: str) -> str:
    first_line = chunk.split("\n", 1)[0]         
    return first_line.rsplit(" b/", 1)[-1]


def _is_ignored(path: str, patterns: list[str]) -> bool:
    name = path.rsplit("/", 1)[-1]
    return any(fnmatch(path, p) or fnmatch(name, p) for p in patterns)


def staged_diff(ignore: list[str] | None = None, max_chars: int = 12000, cwd=None) -> str:
    """Return the staged diff with ignored files removed and size capped."""
    patterns = ignore if ignore is not None else DEFAULT_IGNORE
    raw = run_git("diff", "--cached", "--no-color", "--unified=3", cwd=cwd)
    chunks = re.split(r"(?m)^(?=diff --git )", raw)
    kept = [c for c in chunks if c.strip() and not _is_ignored(_path_from_chunk(c), patterns)]
    diff = "".join(kept)
    if len(diff) > max_chars:
        diff = diff[:max_chars] + "\n[diff truncated]\n"
    return diff