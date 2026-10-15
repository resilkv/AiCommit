import json

import boto3
from botocore.config import Config
from botocore.exceptions import BotoCoreError, ClientError

from .base import LLMError


class BedrockClient:
    """Amazon Nova via InvokeModel. The only file that knows Nova's request/response format."""

    def __init__(self, model_id: str, region: str, max_tokens: int = 300):
        self.model_id = model_id
        self.max_tokens = max_tokens
        self._client = boto3.client(
            "bedrock-runtime",
            region_name=region,
            config=Config(retries={"max_attempts": 0}, connect_timeout=5, read_timeout=30),
        )

    def generate(self, system: str, user: str) -> str:
        body = {
            "system": [{"text": system}],
            "messages": [{"role": "user", "content": [{"text": user}]}],
            "inferenceConfig": {"maxTokens": self.max_tokens, "temperature": 0.2},
        }
        try:
            resp = self._client.invoke_model(
                modelId=self.model_id,
                body=json.dumps(body),
                contentType="application/json",
                accept="application/json",
            )
            data = json.loads(resp["body"].read())
            return data["output"]["message"]["content"][0]["text"]
        except (BotoCoreError, ClientError, KeyError, IndexError, json.JSONDecodeError) as e:
            raise LLMError(f"{type(e).__name__}: {e}") from e