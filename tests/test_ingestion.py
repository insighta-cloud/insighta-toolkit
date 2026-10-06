from __future__ import annotations

import io
import json

from insighta_toolkit.ingestion import ingest_records


class FakeS3:
    def __init__(self):
        self.objects = []

    def put_object(self, **kwargs):
        self.objects.append(kwargs)


class FakeS3Vectors:
    def __init__(self):
        self.requests = []

    def put_vectors(self, **kwargs):
        self.requests.append(kwargs)


class FakeBedrock:
    def __init__(self):
        self.requests = []

    def invoke_model(self, **kwargs):
        self.requests.append(kwargs)
        return {"body": io.BytesIO(json.dumps({"embedding": [0.1, 0.2]}).encode())}


def record(event_id="event-123", language="en"):
    return {
        "id": event_id,
        "language": language,
        "title": "Event title",
        "content": "Event content",
        "tickers": [{"ticker": "ABC"}],
        "urgency_level": "4",
        "sentiment_score": 0.7,
    }


def test_ingestion_writes_source_record_and_vector_with_the_same_stable_key():
    s3 = FakeS3()
    vectors = FakeS3Vectors()
    bedrock = FakeBedrock()

    result = ingest_records(
        [record()],
        records_bucket="records",
        vector_bucket="vectors",
        vector_index="financial-events",
        s3_client=s3,
        s3vectors_client=vectors,
        bedrock_client=bedrock,
    )

    assert result.records_written == 1
    assert result.vectors_written == 1
    assert result.vector_batches == 1
    assert s3.objects[0]["Key"] == "records/event-123/en.json"
    assert json.loads(s3.objects[0]["Body"]) == record()
    assert vectors.requests[0]["vectors"][0]["key"] == "event-123:en"
    metadata = vectors.requests[0]["vectors"][0]["metadata"]
    assert metadata["record_key"] == "records/event-123/en.json"
    assert json.loads(bedrock.requests[0]["body"])["normalize"] is True


def test_ingestion_flushes_progress_in_batches_smaller_than_api_limit():
    s3 = FakeS3()
    vectors = FakeS3Vectors()
    result = ingest_records(
        [record(event_id=f"event-{number}") for number in range(51)],
        records_bucket="records",
        vector_bucket="vectors",
        vector_index="financial-events",
        s3_client=s3,
        s3vectors_client=vectors,
        bedrock_client=FakeBedrock(),
        max_workers=1,
    )

    assert result.vector_batches == 2
    assert [len(request["vectors"]) for request in vectors.requests] == [50, 1]
