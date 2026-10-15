import json

import boto3
from botocore.config import Config
from botocore.exceptions import BotoCoreError, ClientError

from .base import LLMError


class BedrockClient:
    """Amazon Nova via InvokeModel. The only file that knows Nova's request/response format."""

    def __init__(self, model_id: str, region: str, max_tokens: int = 2500):
        self.model_id = model_id
        self.max_tokens = max_tokens
        self._client = boto3.client(
            "bedrock-runtime",
            region_name=region,
            config=Config(retries={"max_attempts": 0}, connect_timeout=5, read_timeout=30),
        )

    def generate(self, system: str, user: str) -> str:
        try:
            resp = self._client.converse(
                modelId=self.model_id,
                system=[{"text": system}],
                messages=[{"role": "user", "content": [{"text": user}]}],
                inferenceConfig={"maxTokens": self.max_tokens, "temperature": 0.2},
            )
            blocks = resp["output"]["message"]["content"]
            return next(b["text"] for b in blocks if "text" in b)
        except (BotoCoreError, ClientError, KeyError, IndexError, StopIteration) as e:
            raise LLMError(f"{type(e).__name__}: {e}") from e