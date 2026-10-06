"""Idempotent JSONL ingestion for the normal S3 and S3 Vectors stores."""

from __future__ import annotations

import argparse
import json
from collections.abc import Iterable, Mapping, Sequence
from concurrent.futures import ThreadPoolExecutor
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Protocol

from insighta_toolkit.vector_documents import VectorDocument, to_vector_document

DEFAULT_EMBEDDING_MODEL_ID = "amazon.titan-embed-text-v2:0"
# The S3 Vectors API accepts up to 500 vectors. A smaller batch keeps useful
# progress if a long ingestion is interrupted.
VECTORS_PER_BATCH = 50
DEFAULT_MAX_WORKERS = 8


class S3Client(Protocol):
    def put_object(self, **kwargs: Any) -> Any: ...


class S3VectorsClient(Protocol):
    def put_vectors(self, **kwargs: Any) -> Any: ...


class BedrockRuntimeClient(Protocol):
    def invoke_model(self, **kwargs: Any) -> Any: ...


@dataclass(frozen=True)
class IngestionResult:
    records_written: int
    vectors_written: int
    vector_batches: int


def load_jsonl(path: Path) -> Iterable[dict[str, Any]]:
    """Yield non-empty JSON object rows from a JSONL file."""

    for line_number, line in enumerate(path.read_text(encoding="utf-8").splitlines(), start=1):
        if not line.strip():
            continue
        value = json.loads(line)
        if not isinstance(value, dict):
            raise ValueError(f"line {line_number} must be a JSON object")
        yield value


def embed_text(client: BedrockRuntimeClient, model_id: str, text: str) -> list[float]:
    """Create a normalized 1,024-dimensional Titan Text Embeddings V2 vector."""

    response = client.invoke_model(
        modelId=model_id,
        contentType="application/json",
        accept="application/json",
        body=json.dumps({"inputText": text, "dimensions": 1024, "normalize": True}),
    )
    payload = json.loads(response["body"].read())
    embedding = payload.get("embedding")
    is_numeric_embedding = isinstance(embedding, list) and all(
        isinstance(value, (int, float)) for value in embedding
    )
    if not is_numeric_embedding:
        raise ValueError("Bedrock embedding response did not contain a numeric embedding")
    return [float(value) for value in embedding]


def ingest_records(
    records: Iterable[Mapping[str, Any]],
    *,
    records_bucket: str,
    vector_bucket: str,
    vector_index: str,
    s3_client: S3Client,
    s3vectors_client: S3VectorsClient,
    bedrock_client: BedrockRuntimeClient,
    model_id: str = DEFAULT_EMBEDDING_MODEL_ID,
    max_workers: int = DEFAULT_MAX_WORKERS,
) -> IngestionResult:
    """Store canonical records, embed them, and upsert vectors in batches.

    The vector key is ``event_id:language``. Re-running the same dataset uses
    that key again, which keeps the ingestion operation idempotent.
    """

    if max_workers < 1:
        raise ValueError("max_workers must be at least 1")

    records_written = 0
    vectors_written = 0
    vector_batches = 0
    batch: list[dict[str, Any]] = []

    def prepare(record: Mapping[str, Any]) -> dict[str, Any]:
        document = to_vector_document(record)
        _put_source_record(s3_client, records_bucket, document, record)
        embedding = embed_text(bedrock_client, model_id, document.text)
        return _to_vector(document, embedding)

    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        for vector in executor.map(prepare, records):
            records_written += 1
            batch.append(vector)

            if len(batch) == VECTORS_PER_BATCH:
                _put_vector_batch(s3vectors_client, vector_bucket, vector_index, batch)
                vectors_written += len(batch)
                vector_batches += 1
                batch = []

    if batch:
        _put_vector_batch(s3vectors_client, vector_bucket, vector_index, batch)
        vectors_written += len(batch)
        vector_batches += 1

    return IngestionResult(records_written, vectors_written, vector_batches)


def _put_source_record(
    client: S3Client,
    bucket: str,
    document: VectorDocument,
    record: Mapping[str, Any],
) -> None:
    client.put_object(
        Bucket=bucket,
        Key=document.metadata["record_key"],
        Body=json.dumps(dict(record), ensure_ascii=False).encode(),
        ContentType="application/json",
    )


def _to_vector(document: VectorDocument, embedding: Sequence[float]) -> dict[str, Any]:
    return {
        "key": document.key,
        "data": {"float32": list(embedding)},
        "metadata": document.metadata,
    }


def _put_vector_batch(
    client: S3VectorsClient, vector_bucket: str, vector_index: str, vectors: list[dict[str, Any]]
) -> None:
    client.put_vectors(vectorBucketName=vector_bucket, indexName=vector_index, vectors=vectors)


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("input", type=Path, help="Input JSONL dataset")
    parser.add_argument("--records-bucket", required=True)
    parser.add_argument("--vector-bucket", required=True)
    parser.add_argument("--vector-index", required=True)
    parser.add_argument("--region", default="us-east-1")
    parser.add_argument("--model-id", default=DEFAULT_EMBEDDING_MODEL_ID)
    parser.add_argument("--max-workers", type=int, default=DEFAULT_MAX_WORKERS)
    args = parser.parse_args()

    import boto3

    result = ingest_records(
        load_jsonl(args.input),
        records_bucket=args.records_bucket,
        vector_bucket=args.vector_bucket,
        vector_index=args.vector_index,
        s3_client=boto3.client("s3", region_name=args.region),
        s3vectors_client=boto3.client("s3vectors", region_name=args.region),
        bedrock_client=boto3.client("bedrock-runtime", region_name=args.region),
        model_id=args.model_id,
        max_workers=args.max_workers,
    )
    print(f"Wrote {result.records_written} records and {result.vectors_written} vectors.")


if __name__ == "__main__":
    main()
