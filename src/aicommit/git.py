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


def _is_ignored(path: str, patterns: list[str]) -> bool:
    name = path.rsplit("/", 1)[-1]
    return any(fnmatch(path, p) or fnmatch(name, p) for p in patterns)


def staged_diff(ignore: list[str] | None = None, max_chars: int = 12000, cwd=None) -> str:
    """Return the staged diff with ignored files removed and size capped."""
    patterns = ignore if ignore is not None else DEFAULT_IGNORE
    # Use Git's path filtering, which handles quoted filenames itself. Apply
    # patterns against both paths so renames cannot leak an ignored old path.
    paths = run_git("diff", "--cached", "--name-only", "-z", cwd=cwd).split("\0")
    paths = [path for path in paths if path]
    kept = [path for path in paths if not _is_ignored(path, patterns)]
    if not kept:
        return ""
    raw = subprocess.run(
        ["git", "diff", "--cached", "--no-color", "--unified=3", "--", *kept],
        capture_output=True,
        text=True,
        check=True,
        cwd=cwd,
    ).stdout
    diff = raw
    if len(diff) > max_chars:
        diff = diff[:max_chars] + "\n[diff truncated]\n"
    return diff
