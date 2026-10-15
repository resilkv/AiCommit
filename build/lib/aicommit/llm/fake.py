CANNED = '{"type": "chore", "scope": null, "subject": "update files (fake provider)", "body": null}'


class FakeLLM:
    """Returns queued responses in order; the last one repeats. Used by tests and demos."""

    def __init__(self, responses: list[str] | None = None):
        self.responses = list(responses) if responses else [CANNED]
        self.calls = 0

    def generate(self, system: str, user: str) -> str:
        i = min(self.calls, len(self.responses) - 1)
        self.calls += 1
        return self.responses[i]