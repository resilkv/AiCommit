from typing import Protocol


class LLMError(Exception):
    """Any failure talking to a model (network, quota, bad response shape)."""


class LLMClient(Protocol):
    def generate(self, system: str, user: str) -> str: ...