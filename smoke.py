import boto3
import json
from dotenv import load_dotenv

load_dotenv()




client = boto3.client("bedrock-runtime", region_name="ap-southeast-2")

response = client.invoke_model(
    body=json.dumps({
            'messages': [{
                'role': 'user',
                'content': [{'text':  "Write a commit message for: fix null check in login view"}]
            }],
            'inferenceConfig': {
                'maxTokens': 1024
            }
    }),
    contentType='application/json',
    accept='application/json',
    modelId='amazon.nova-pro-v1:0',
    trace='ENABLED',
    # guardrailIdentifier='string',
    # guardrailVersion='string',
    performanceConfigLatency='standard',
    # serviceTier='priority'|'default'|'flex'|'reserved',
    # requestMetadata='string'
)

data = json.loads(response["body"].read())
print(data["output"]["message"]["content"][0]["text"])
