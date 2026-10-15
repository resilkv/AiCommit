import pytest

from aicommit.llm.fake import FakeLLM
from aicommit.pipeline import InvalidModelOutput, generate_message

GOOD = '{"type": "fix", "scope": "auth", "subject": "add null check in login view", "body": null}'


def test_valid_json():
    msg = generate_message(FakeLLM([GOOD]), "diff")
    assert msg.render() == "fix(auth): add null check in login view\n"


def test_json_wrapped_in_prose_and_fences():
    llm = FakeLLM([f"Here you go:\n```json\n{GOOD}\n```"])
    assert generate_message(llm, "diff").type == "fix"


def test_retries_once_then_succeeds():
    llm = FakeLLM(["not json at all", GOOD])
    assert generate_message(llm, "diff").scope == "auth"
    assert llm.calls == 2


def test_gives_up_after_retries():
    llm = FakeLLM(["nope"])
    with pytest.raises(InvalidModelOutput):
        generate_message(llm, "diff")
    assert llm.calls == 2


def test_rejects_unknown_type():
    bad = '{"type": "wizardry", "subject": "x"}'
    with pytest.raises(InvalidModelOutput):
        generate_message(FakeLLM([bad]), "diff")