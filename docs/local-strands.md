# Local Strands quick start

The local application is a separate runnable app at `apps/local`. Records,
vector search, and the Strands process run locally with `sqlite-vec`; only the
chat and embedding models are called through a configured remote API. It does
not require AgentCore, S3, or S3 Vectors.

## Prerequisites

- [uv](https://docs.astral.sh/uv/)
- Credentials for Amazon Bedrock, OpenAI, or Azure OpenAI

Choose a provider with environment variables. Bedrock is the default:

```bash
export AWS_PROFILE=<your-profile>
uv sync --extra local
```

## Index and chat

The database defaults to `.local/insighta.db`; it is intentionally ignored by
Git. Re-run `index` after changing the dataset or embedding model.

```bash
uv run --extra local python -m apps.local.main index sample/202608_60x3.jsonl
uv run --extra local python -m apps.local.main chat "최근 고긴급 이벤트를 요약해줘"
```

Use `--region` to choose a Bedrock Region and `--database` to use another
SQLite file. Embedding dimensions are bound to the database at its first
index; use a new database path when changing embedding models.

## Model provider configuration

| Provider | Required configuration | Default chat / embedding model |
| --- | --- | --- |
| Bedrock | Standard AWS credential chain; optional `AWS_REGION` | Claude Sonnet 4.5 / Titan Text Embeddings V2 |
| OpenAI | `INSIGHTA_MODEL_PROVIDER=openai`, `OPENAI_API_KEY` | `gpt-4.1-mini` / `text-embedding-3-small` |
| Azure OpenAI | `INSIGHTA_MODEL_PROVIDER=azure-openai`, `AZURE_OPENAI_ENDPOINT`, `AZURE_OPENAI_API_KEY`, `AZURE_OPENAI_CHAT_DEPLOYMENT`, `AZURE_OPENAI_EMBEDDING_DEPLOYMENT` | Your deployments |

Override the model names with `CHAT_MODEL_ID` and `EMBEDDING_MODEL_ID`, or the
equivalent `--chat-model` and `--embedding-model` command options. For
OpenAI-compatible gateways, set `OPENAI_BASE_URL`.
