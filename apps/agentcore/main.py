"""AgentCore Runtime entrypoint for the Insighta Strands agent."""

from __future__ import annotations

import os
from typing import Any

import boto3
from bedrock_agentcore import BedrockAgentCoreApp
from strands import Agent, tool
from strands.models import BedrockModel

from insighta_toolkit.ingestion import DEFAULT_EMBEDDING_MODEL_ID, embed_text
from insighta_toolkit.retrieval import FinancialEventRetriever

app = BedrockAgentCoreApp()


def create_agent() -> Agent:
    """Create the AgentCore agent and its scoped financial retrieval tool."""

    region = os.environ["AWS_REGION"]
    retriever = FinancialEventRetriever(
        records_bucket=os.environ["RECORDS_BUCKET"],
        vector_bucket=os.environ["VECTOR_BUCKET"],
        vector_index=os.environ["VECTOR_INDEX"],
        s3_client=boto3.client("s3", region_name=region),
        s3vectors_client=boto3.client("s3vectors", region_name=region),
        embed=lambda text: embed_text(
            boto3.client("bedrock-runtime", region_name=region),
            os.environ.get("EMBEDDING_MODEL_ID", DEFAULT_EMBEDDING_MODEL_ID),
            text,
        ),
    )

    @tool
    def retrieve_financial_events(
        query: str,
        language: str | None = None,
        ticker: str | None = None,
        top_k: int = 5,
    ) -> list[dict[str, Any]]:
        """Search financial events. Filter by en, ko, or ja language and a ticker when useful."""

        return retriever.search(query, language=language, ticker=ticker, top_k=top_k)

    model = BedrockModel(model_id=os.environ["CHAT_MODEL_ID"], region_name=region)
    return Agent(
        model=model,
        tools=[retrieve_financial_events],
        system_prompt=(
            "You are a financial intelligence assistant. Use retrieve_financial_events for "
            "dataset-backed claims, identify uncertainty, and cite each event's source URL. "
            "Do not provide personalized investment advice."
        ),
    )


@app.entrypoint
async def handler(request: dict[str, Any]) -> dict[str, str]:
    prompt = request.get("prompt")
    if not isinstance(prompt, str) or not prompt.strip():
        raise ValueError("prompt must be a non-empty string")
    if prompt == "__healthcheck__":
        return {"response": "ok"}
    return {"response": str(create_agent()(prompt))}


if __name__ == "__main__":
    app.run()
