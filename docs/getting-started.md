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

## Clean up

Destroy only the resources from the exact `infra/` state you intend to retire.
`tofu destroy` removes the AgentCore runtime, IAM roles, S3 Vectors resources,
and the records bucket defined by this root. It cannot remove a non-empty S3
bucket automatically.

First inspect the plan. If the records bucket contains only data you intend to
delete, empty that exact bucket, then run the destroy operation. Emptying a
bucket permanently removes its objects.

```bash
cd infra
tofu plan -destroy
records_bucket="$(tofu output -raw records_bucket_name)"
aws s3 rm "s3://${records_bucket}" --recursive
tofu destroy
```

Do not run these commands against a shared or production state until you have
confirmed the account, Region, state backend, and bucket name.
