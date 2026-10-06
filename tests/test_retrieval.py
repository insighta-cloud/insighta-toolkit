from __future__ import annotations

import io
import json

from insighta_toolkit.retrieval import FinancialEventRetriever


class FakeS3:
    def get_object(self, **kwargs):
        assert kwargs == {"Bucket": "records", "Key": "records/event-123/ko.json"}
        return {"Body": io.BytesIO(json.dumps({"id": "event-123", "language": "ko"}).encode())}


class FakeS3Vectors:
    def __init__(self):
        self.request = None

    def query_vectors(self, **kwargs):
        self.request = kwargs
        return {
            "vectors": [
                {
                    "key": "event-123:ko",
                    "distance": 0.12,
                    "metadata": {"record_key": "records/event-123/ko.json"},
                }
            ]
        }


def test_retrieves_canonical_record_with_language_and_ticker_filter():
    vectors = FakeS3Vectors()
    retriever = FinancialEventRetriever(
        records_bucket="records",
        vector_bucket="vectors",
        vector_index="financial-events",
        s3_client=FakeS3(),
        s3vectors_client=vectors,
        embed=lambda query: [0.1, 0.2],
    )

    results = retriever.search("삼성 관련 이벤트", language="ko", ticker="abc")

    assert results == [{"record": {"id": "event-123", "language": "ko"}, "distance": 0.12}]
    assert vectors.request["queryVector"] == {"float32": [0.1, 0.2]}
    assert vectors.request["filter"] == {
        "$and": [{"language": {"$eq": "ko"}}, {"tickers": {"$eq": "ABC"}}]
    }
