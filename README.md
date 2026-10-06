# Insighta Toolkit

[English](README.md) | [한국어](README.ko.md) | [日本語](README.ja.md)

![Local terminal: a high-urgency PFE query retrieves an event and prints its White House source URL](assets/local-bedrock-cli-demo.png)

Insighta Toolkit is a reference implementation for building a financial-event
retrieval application. It turns a JSONL file of multilingual events into
searchable evidence, then lets a user ask questions whose answers can cite the
underlying source URLs.

It is deliberately a toolkit: it shows the application shape, retrieval
contract, and deployment choices that a team can adapt to its own data and
models. The included JSONL is a small fixture for trying the code, not the
purpose of this repository.

## What you can run

The repository contains two implementations of the same workflow.

| Path | What runs | Best for |
| --- | --- | --- |
| **Local Strands + Bedrock** | JSONL records and vector search stay in a local SQLite database; Bedrock provides embeddings and chat. | Trying the workflow on one machine and inspecting retrieval results directly. |
| **AWS AgentCore** | A Strands retrieval agent runs in AgentCore Runtime; OpenTofu provisions S3 and S3 Vectors. | A deployable AWS reference architecture. |

Both paths answer from retrieved records rather than treating a model response
as a source of truth. Every result retains the original event URL so a user can
open and verify the cited material.

## How it works

```text
JSONL event records
        │
        ├── validate id, language, title, content, and metadata
        ├── create one searchable document per language
        ├── embed title + content
        └── retrieve relevant records for a question
                                      │
                                      ▼
                         Strands agent response
                         with source URLs to verify
```

The shared record contract gives each logical event an `id`, a language-specific
`title` and `content`, ticker metadata, urgency and sentiment fields, and source
provenance. The local and AWS paths use that same contract, so an application
can move between them without redesigning its input shape.

## Start locally

The local app is the fastest way to understand the Toolkit. Configure AWS
credentials that can use the selected Bedrock models, then index the sample and
ask a question:

```bash
export AWS_PROFILE=<your-profile>
uv sync --extra local
uv run --extra local python -m apps.local.main index sample/202608_60x3.jsonl
uv run --extra local python -m apps.local.main chat "Summarize high-urgency events and cite the source URLs."
```

The terminal makes the retrieval step visible: the question calls the financial
event search tool, produces a concise answer, and returns the URL that supports
it. It is the fastest way to see whether your data, embedding model, and
retrieval settings produce useful evidence.

When you take the workflow into an application, keep that evidence visible: a
readable answer should retain retrieved-source references for inspection.

![Hosted financial-research response: a market-sentiment answer with visible source trace references](assets/bedrock-agent-demo.png)

The index is stored in `.local/insighta.db`; it is local-only and ignored by
Git. The [local quick start](docs/local-strands.md) explains provider settings,
database selection, and model overrides.

## Deploy the AWS reference path

The AWS path packages `apps/agentcore`, provisions the runtime and vector
storage with OpenTofu, then ingests the same JSONL contract. It is intended as
an infrastructure and application reference, not as a replacement for an
organization's access controls, monitoring, or data governance.

Follow the [AWS AgentCore quick start](docs/getting-started.md) for the exact
prerequisites, build, deployment, ingestion, and invocation sequence.

For a user-facing application, preserve the same evidence-grounded interaction:
a readable answer with retrieved-source references available for inspection,
rather than an untraceable model claim.

## Included sample

[`sample/202608_60x3.jsonl`](sample/202608_60x3.jsonl) is a compact,
multilingual test fixture for the Toolkit. It contains 60 logical events and
180 records: one English (`en`), Korean (`ko`), and Japanese (`ja`) record per
event. Use it to confirm that your environment can:

- parse UTF-8 JSONL;
- retrieve the same event across three languages;
- filter or rank by ticker and urgency metadata; and
- return a source URL with an answer.

Each line is a public event record with these core fields:

| Fields | Purpose in the Toolkit |
| --- | --- |
| `id`, `language` | Align the three language records for one event. |
| `title`, `content` | Supply the text sent to the embedding and retrieval layers. |
| `tickers`, `urgency_level`, `sentiment_score` | Support structured filtering and ranking. |
| `source`, `source_name`, `author`, `created_at` | Let an application present provenance alongside an answer. |

The sample is an evaluation asset, not a real-time feed or investment advice.
For consequential use, verify any generated answer against the linked primary
source.

## Repository layout

```text
apps/local/       Local Strands application and SQLite vector store
apps/agentcore/   AgentCore Runtime entrypoint
infra/            OpenTofu configuration for the AWS reference path
src-python/       Shared JSONL ingestion, retrieval, and document helpers
sample/           Public JSONL fixture
docs/             Local and AWS quick starts
tests/            Unit tests for the shared retrieval contract
```

## License

SEE LICENSE IN [LICENSE](LICENSE).

## Clean up AWS resources

If you deployed the AWS reference path, clean it up from the same `infra/`
state that created it. Review `tofu plan -destroy` first. The records bucket
must be emptied before `tofu destroy` can remove it, and emptying it permanently
deletes its objects. See the [AWS cleanup instructions](docs/getting-started.md#clean-up)
before running either command.

## About insighta cloud

We are building an investment workstation for individuals — giving personal
investors institutional-grade processes and tools. Learn more at
[insighta.cloud/landing](https://insighta.cloud/landing).

## Contact

- **Provider:** insighta cloud Inc.
- **Website:** [https://insighta.cloud](https://insighta.cloud)
- **Contact:** support@insighta.cloud
- **AWS Marketplace:** [seller profile](https://aws.amazon.com/marketplace/seller-profile?id=seller-ahk55ljrhr4wu)
- **Datarade provider profile:** [insighta cloud Inc.](https://datarade.ai/data-providers/insighta-cloud-inc/profile)
- **LinkedIn:** [cho-insighta-cloud](https://www.linkedin.com/in/cho-insighta-cloud/)

## Author

insighta cloud Inc.
