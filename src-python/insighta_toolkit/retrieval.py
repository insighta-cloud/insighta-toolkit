"""S3 Vectors retrieval with canonical records loaded from standard S3."""

from __future__ import annotations

import json
from collections.abc import Callable
from dataclasses import dataclass
from typing import Any, Protocol


class S3Client(Protocol):
    def get_object(self, **kwargs: Any) -> Any: ...


class S3VectorsClient(Protocol):
    def query_vectors(self, **kwargs: Any) -> Any: ...


@dataclass
class FinancialEventRetriever:
    """Retrieves vectors and resolves their canonical S3 source records."""

    records_bucket: str
    vector_bucket: str
    vector_index: str
    s3_client: S3Client
    s3vectors_client: S3VectorsClient
    embed: Callable[[str], list[float]]

    def search(
        self,
        query: str,
        *,
        language: str | None = None,
        ticker: str | None = None,
        top_k: int = 5,
    ) -> list[dict[str, Any]]:
        """Return source records relevant to a query and optional metadata filters."""

        if not query.strip():
            raise ValueError("query must be a non-empty string")
        if not 1 <= top_k <= 10:
            raise ValueError("top_k must be between 1 and 10")

        request: dict[str, Any] = {
            "vectorBucketName": self.vector_bucket,
            "indexName": self.vector_index,
            "topK": top_k,
            "queryVector": {"float32": self.embed(query)},
            "returnMetadata": True,
            "returnDistance": True,
        }
        metadata_filter = _metadata_filter(language=language, ticker=ticker)
        if metadata_filter:
            request["filter"] = metadata_filter

        response = self.s3vectors_client.query_vectors(**request)
        return [self._source_record(vector) for vector in response.get("vectors", [])]

    def _source_record(self, vector: dict[str, Any]) -> dict[str, Any]:
        metadata = vector.get("metadata", {})
        record_key = metadata.get("record_key")
        if not isinstance(record_key, str):
            raise ValueError("S3 Vectors response is missing record_key metadata")

        response = self.s3_client.get_object(Bucket=self.records_bucket, Key=record_key)
        record = json.loads(response["Body"].read())
        if not isinstance(record, dict):
            raise ValueError(f"source object {record_key} must contain a JSON object")
        return {"record": record, "distance": vector.get("distance")}


def _metadata_filter(*, language: str | None, ticker: str | None) -> dict[str, Any] | None:
    filters = []
    if language:
        filters.append({"language": {"$eq": language}})
    if ticker:
        # $eq against a list-valued metadata field matches a list member.
        filters.append({"tickers": {"$eq": ticker.upper()}})
    if not filters:
        return None
    return filters[0] if len(filters) == 1 else {"$and": filters}
