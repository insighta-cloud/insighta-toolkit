"""Run the local Ollama + Strands financial assistant."""

from __future__ import annotations

import argparse
import os
from collections.abc import Sequence
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path
from typing import Any

import boto3
from openai import AzureOpenAI, OpenAI
from strands import Agent, tool
from strands.models import BedrockModel
from strands.models.openai import OpenAIModel

from apps.local.vector_store import LocalVectorStore
from insighta_toolkit.ingestion import DEFAULT_EMBEDDING_MODEL_ID, embed_text, load_jsonl
from insighta_toolkit.vector_documents import to_vector_document

DEFAULT_BEDROCK_CHAT_MODEL = "us.anthropic.claude-sonnet-4-5-20250929-v1:0"


def embed(
    provider: str, client: Any, model: str, texts: str | list[str], *, max_workers: int = 8
) -> list[list[float]]:
    """Embed one or more texts through the configured remote model provider."""

    values = [texts] if isinstance(texts, str) else texts
    if provider == "bedrock":
        with ThreadPoolExecutor(max_workers=max_workers) as executor:
            return list(executor.map(lambda value: embed_text(client, model, value), values))
    response = client.embeddings.create(model=model, input=values)
    return [[float(value) for value in item.embedding] for item in response.data]


def index_dataset(
    input_path: Path,
    database: Path,
    provider: str,
    client: Any,
    embedding_model: str,
) -> int:
    """Embed a JSONL release and write it into a local SQLite vector database."""

    records = list(load_jsonl(input_path))
    if not records:
        raise ValueError("input dataset has no records")
    texts = [to_vector_document(record).text for record in records]
    embeddings = embed(provider, client, embedding_model, texts)
    if len(embeddings) != len(records):
        raise ValueError("embedding provider returned a different number of embeddings")
    store = LocalVectorStore(database, dimensions=len(embeddings[0]))
    try:
        for record, vector in zip(records, embeddings, strict=True):
            store.upsert(record, vector)
    finally:
        store.close()
    return len(records)


def create_agent(
    store: LocalVectorStore,
    provider: str,
    client: Any,
    region: str,
    chat_model: str,
    embedding_model: str,
) -> Agent:
    """Create a local Strands agent with a remote-model retrieval tool."""

    @tool
    def retrieve_financial_events(
        query: str, language: str | None = None, ticker: str | None = None, top_k: int = 5
    ) -> list[dict[str, Any]]:
        """Search financial events. Filter by en, ko, or ja language and a ticker when useful."""

        return store.search(
            embed(provider, client, embedding_model, query)[0],
            language=language,
            ticker=ticker,
            top_k=top_k,
        )

    model: Any = (
        BedrockModel(model_id=chat_model, region_name=region)
        if provider == "bedrock"
        else OpenAIModel(client=client, model_id=chat_model)
    )
    return Agent(
        model=model,
        tools=[retrieve_financial_events],
        system_prompt=(
            "You are a financial intelligence assistant. Use retrieve_financial_events for "
            "dataset-backed claims, identify uncertainty, and cite each event's source URL. "
            "Do not provide personalized investment advice."
        ),
    )


def main(argv: Sequence[str] | None = None) -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--provider",
        choices=("bedrock", "openai", "azure-openai"),
        default=os.environ.get("INSIGHTA_MODEL_PROVIDER", "bedrock"),
    )
    parser.add_argument("--region", default=os.environ.get("AWS_REGION", "us-east-1"))
    subparsers = parser.add_subparsers(dest="command", required=True)
    index_parser = subparsers.add_parser("index", help="Index a JSONL dataset into SQLite")
    index_parser.add_argument("input", type=Path)
    index_parser.add_argument("--database", type=Path, default=Path(".local/insighta.db"))
    index_parser.add_argument("--embedding-model")
    chat_parser = subparsers.add_parser("chat", help="Chat with the local Strands agent")
    chat_parser.add_argument("--database", type=Path, default=Path(".local/insighta.db"))
    chat_parser.add_argument("--chat-model")
    chat_parser.add_argument("--embedding-model")
    chat_parser.add_argument("prompt")
    args = parser.parse_args(argv)
    if args.provider == "bedrock":
        client: Any = boto3.client("bedrock-runtime", region_name=args.region)
        default_embedding_model = DEFAULT_EMBEDDING_MODEL_ID
        default_chat_model = DEFAULT_BEDROCK_CHAT_MODEL
    elif args.provider == "openai":
        client = OpenAI(base_url=os.environ.get("OPENAI_BASE_URL"))
        default_embedding_model = "text-embedding-3-small"
        default_chat_model = "gpt-4.1-mini"
    else:
        client = AzureOpenAI(
            azure_endpoint=os.environ["AZURE_OPENAI_ENDPOINT"],
            api_version=os.environ.get("AZURE_OPENAI_API_VERSION", "2024-10-21"),
        )
        default_embedding_model = os.environ["AZURE_OPENAI_EMBEDDING_DEPLOYMENT"]
        default_chat_model = os.environ["AZURE_OPENAI_CHAT_DEPLOYMENT"]
    embedding_model = args.embedding_model or os.environ.get(
        "EMBEDDING_MODEL_ID", default_embedding_model
    )
    if args.command == "index":
        count = index_dataset(args.input, args.database, args.provider, client, embedding_model)
        print(f"Indexed {count} records.")
        return
    healthcheck_embedding = embed(args.provider, client, embedding_model, "healthcheck")[0]
    store = LocalVectorStore(args.database, dimensions=len(healthcheck_embedding))
    try:
        chat_model = args.chat_model or os.environ.get("CHAT_MODEL_ID", default_chat_model)
        agent = create_agent(
            store,
            args.provider,
            client,
            args.region,
            chat_model,
            embedding_model,
        )
        agent(args.prompt)
    finally:
        store.close()


if __name__ == "__main__":
    main()
