# OpenTofu + AgentCore quick start

This is the supported deployment path. It uses normal S3 for canonical event
records, S3 Vectors for retrieval, and an AgentCore Runtime hosting a Strands
agent. It creates neither OpenSearch nor a Bedrock Knowledge Base.

## Prerequisites

- `uv`, OpenTofu, and AWS CLI credentials for a Region supporting S3 Vectors
  and the configured Bedrock models.
- Bedrock model access for Titan Text Embeddings V2 and Claude Sonnet 4.5.

Select AWS credentials through the standard credential chain. For example, set
`AWS_PROFILE=<your-profile>` in your shell; no profile name is embedded in the
toolkit.

## Deploy

```bash
uv sync
uv run ruff check .
uv run pytest
uv run python tools/build_runtime_bundle.py

cd infra
tofu init
tofu fmt -check -recursive
tofu validate
tofu plan
tofu apply
```

## Index the sample data

From `infra/`, run:

```bash
uv run python -m insighta_toolkit.ingestion ../sample/202608_60x3.jsonl \
  --region us-east-1 \
  --records-bucket "$(tofu output -raw records_bucket_name)" \
  --vector-bucket "$(tofu output -raw vector_bucket_name)" \
  --vector-index financial-events
```

## Invoke the runtime

Use the AgentCore Runtime ARN from `tofu output -raw agent_runtime_arn` with
the AgentCore invocation API. See [agentcore-runtime.md](agentcore-runtime.md)
for the payload contract.
