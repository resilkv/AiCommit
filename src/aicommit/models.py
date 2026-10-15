from typing import Literal

from pydantic import BaseModel, Field


class CommitMessage(BaseModel):
    type: Literal["feat", "fix", "docs", "style", "refactor", "perf", "test", "build", "ci", "chore"]
    scope: str | None = None
    subject: str = Field(min_length=1, max_length=72)
    body: str | None = None

    def render(self) -> str:
        head = f"{self.type}({self.scope}): {self.subject}" if self.scope else f"{self.type}: {self.subject}"
        if self.body and self.body.strip():
            return f"{head}\n\n{self.body.strip()}\n"
        return f"{head}\n"