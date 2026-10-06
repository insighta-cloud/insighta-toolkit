"""Convert Insighta JSONL records into stable S3 Vectors documents.

This module deliberately has no AWS dependency.  It lets us verify the data
contract before provisioning a vector bucket in the next migration phase.
"""

from __future__ import annotations

from collections.abc import Iterable, Mapping
from dataclasses import dataclass
from typing import Any


@dataclass(frozen=True)
class VectorDocument:
    """The text, key, and filterable metadata for one embedded record."""

    key: str
    text: str
    metadata: dict[str, Any]


def to_vector_documents(records: Iterable[Mapping[str, Any]]) -> list[VectorDocument]:
    """Create one language-specific vector document per valid dataset record.

    `content` remains the embedding input only.  A later ingestion step will
    put the complete source record in the standard S3 data bucket and retain
    only compact retrieval metadata in S3 Vectors.
    """

    return [to_vector_document(record) for record in records]


def to_vector_document(record: Mapping[str, Any]) -> VectorDocument:
    """Validate and normalize a public dataset row for vector ingestion."""

    event_id = _required_string(record, "id")
    language = _required_string(record, "language")
    title = _required_string(record, "title")
    content = _required_string(record, "content")

    tickers = sorted(
        {
            ticker["ticker"]
            for ticker in record.get("tickers", [])
            if isinstance(ticker, Mapping) and isinstance(ticker.get("ticker"), str)
        }
    )
    metadata = {
        "event_id": event_id,
        "language": language,
        "tickers": tickers,
        "urgency_level": _number_or_none(record.get("urgency_level")),
        "sentiment_score": _number_or_none(record.get("sentiment_score")),
        "source_name": _string_or_none(record.get("source_name")),
        "created_at": _string_or_none(record.get("created_at")),
        "record_key": f"records/{event_id}/{language}.json",
    }
    return VectorDocument(
        key=f"{event_id}:{language}",
        text=f"{title}\n\n{content}",
        metadata={
            key: value for key, value in metadata.items() if value is not None and value != []
        },
    )


def _required_string(record: Mapping[str, Any], key: str) -> str:
    value = record.get(key)
    if not isinstance(value, str) or not value.strip():
        raise ValueError(f"record field '{key}' must be a non-empty string")
    return value.strip()


def _string_or_none(value: Any) -> str | None:
    return value.strip() if isinstance(value, str) and value.strip() else None


def _number_or_none(value: Any) -> float | None:
    if value is None:
        return None
    try:
        return float(value)
    except (TypeError, ValueError):
        return None
