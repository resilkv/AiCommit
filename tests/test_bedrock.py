import json
from io import BytesIO

from aicommit.llm import bedrock
from aicommit.llm.bedrock import BedrockClient


def test_generate_sends_configured_max_tokens(monkeypatch):
    calls = []

    class FakeRuntime:
        def invoke_model(self, **kwargs):
            calls.append(kwargs)
            return {
                "body": BytesIO(
                    b'{"output":{"message":{"content":[{"text":"response"}]}}}'
                )
            }

    monkeypatch.setattr(bedrock.boto3, "client", lambda *args, **kwargs: FakeRuntime())
    client = BedrockClient("amazon.nova-pro-v1:0", "ap-southeast-2", max_tokens=2500)

    assert client.generate("system", "user") == "response"
    request_body = json.loads(calls[0]["body"])
    assert request_body["inferenceConfig"]["maxTokens"] == 2500
