import tomllib
from dataclasses import dataclass, fields
from pathlib import Path


@dataclass
class Config:
    model_id: str = "amazon.nova-lite-v1:0"
    region: str = "ap-southeast-2"
    max_diff_chars: int = 12000
    ignore: list[str] | None = None   # None = use DEFAULT_IGNORE


def load_config(path: str = ".aicommit.toml") -> Config:
    p = Path(path)
    data = tomllib.loads(p.read_text()) if p.exists() else {}
    allowed = {f.name for f in fields(Config)}
    return Config(**{k: v for k, v in data.items() if k in allowed})