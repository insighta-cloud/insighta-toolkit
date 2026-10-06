from __future__ import annotations

import pytest
from apps.local.vector_store import LocalVectorStore


def _record(identifier: str, language: str, ticker: str) -> dict[str, object]:
    return {
        "id": identifier,
        "language": language,
        "title": f"{ticker} update",
        "content": "Financial event",
        "tickers": [{"ticker": ticker}],
    }


def test_persists_and_filters_nearest_records(tmp_path):
    store = LocalVectorStore(tmp_path / "events.db", dimensions=2)
    try:
        store.upsert(_record("one", "en", "abc"), [1.0, 0.0])
        store.upsert(_record("two", "ko", "xyz"), [0.0, 1.0])

        results = store.search([0.9, 0.1], language="en", ticker="ABC")
        assert results[0]["record"] == _record("one", "en", "abc")
        assert results[0]["distance"] == pytest.approx(0.006116, rel=1e-3)
    finally:
        store.close()
