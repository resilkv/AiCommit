from pydantic import ValidationError

from aicommit.llm.base import LLMClient
from aicommit.models import CommitMessage
from aicommit.prompts import SYSTEM_PROMPT, user_prompt



class InvalidModelOutput(Exception):
    pass


def _extract_json(text: str) -> str:
    start, end = text.find("{"), text.rfind("}")
    if start == -1 or end <= start:
        raise ValueError("no JSON object in reply")
    return text[start : end + 1]


def generate_message(llm: LLMClient, diff: str, retries: int = 1) -> CommitMessage:
    prompt = user_prompt(diff)
    last_error: Exception | None = None
    for _ in range(retries + 1):
        raw = llm.generate(SYSTEM_PROMPT, prompt)
        try:
            return CommitMessage.model_validate_json(_extract_json(raw))
        except (ValueError, ValidationError) as e:   # ValidationError is a ValueError too
            last_error = e
            prompt += "\n\nYour previous reply was not valid JSON for the schema. Reply with the JSON object only."
    raise InvalidModelOutput(f"model output invalid after {retries + 1} tries: {last_error}")