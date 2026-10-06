# AgentCore Runtime operation

The OpenTofu runtime packages `apps/agentcore/` plus the shared `src-python/` package and uploads it to the private
records bucket. The application has one Strands tool:
`retrieve_financial_events`. It embeds the query, filters and queries S3
Vectors, then loads the canonical event record from standard S3.

## Deploy and ingest

After configuring AWS credentials for a Region that supports both S3 Vectors
and the chosen Bedrock models:

```bash
uv run python tools/build_runtime_bundle.py
cd infra
tofu init
tofu plan
tofu apply

uv run python -m insighta_toolkit.ingestion ../sample/202608_60x3.jsonl \
  --region us-east-1 \
  --records-bucket "$(tofu output -raw records_bucket_name)" \
  --vector-bucket "$(tofu output -raw vector_bucket_name)" \
  --vector-index financial-events
```

## Invoke

Use the AgentCore runtime invocation API with the `agent_runtime_arn` output
and JSON payload below. The deployed runtime accepts a non-empty `prompt`.

```json
{"prompt":"한국어로 최근 높은 긴급도 금융 이벤트를 요약해줘"}
```

The runtime response is a JSON object with a `response` string. Validate
retrieval citations against the source URLs in each returned event.
