# Insighta Toolkit

[English](README.md) | [한국어](README.ko.md) | [日本語](README.ja.md)

Evaluate the included multilingual financial-event JSONL sample through either
of the supported applications.

## Choose a path

| AWS AgentCore | Local Strands + Bedrock |
| --- | --- |
| Deploy a Strands retrieval agent with OpenTofu, S3 Vectors, and AgentCore Runtime. | Keep the JSONL records and vector index in a local SQLite database while using Bedrock for embeddings and chat. |
| [AWS quick start](docs/getting-started.md) | [Local quick start](docs/local-strands.md) |

Both paths use the same public JSONL schema and preserve source URLs for
evidence-grounded answers.

## Sample dataset

The included sample contains 60 aligned events (180 English, Korean, and
Japanese records). It demonstrates the public JSONL schema, source grounding,
ticker mappings, sentiment, and urgency fields.

The complete **US Financial Events: SEC & Government Sources, Multilingual
AI-Ready Dataset** is available through
[Datarade](https://datarade.ai/data-products/us-financial-events-sec-government-sources-multilingual-a-insighta-cloud-inc).
For licensed dataset or API access, contact support@insighta.cloud.

## License

See [LICENSE](LICENSE).

## Contact

insighta cloud Inc. · [insighta.cloud](https://insighta.cloud) · support@insighta.cloud
