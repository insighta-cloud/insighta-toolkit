from insighta_toolkit.vector_documents import to_vector_document


def test_creates_a_language_specific_document_with_filterable_metadata():
    document = to_vector_document(
        {
            "id": "event-123",
            "language": "ko",
            "title": "실적 발표",
            "content": "회사는 매출 증가를 발표했습니다.",
            "tickers": [{"ticker": "ABC"}, {"ticker": "ABC"}, {"ticker": "XYZ"}],
            "urgency_level": "4.0",
            "sentiment_score": 0.75,
            "source_name": "sec",
            "created_at": "2026-08-31T00:00:00+00:00",
        }
    )

    assert document.key == "event-123:ko"
    assert document.text == "실적 발표\n\n회사는 매출 증가를 발표했습니다."
    assert document.metadata == {
        "event_id": "event-123",
        "language": "ko",
        "tickers": ["ABC", "XYZ"],
        "urgency_level": 4.0,
        "sentiment_score": 0.75,
        "source_name": "sec",
        "created_at": "2026-08-31T00:00:00+00:00",
        "record_key": "records/event-123/ko.json",
    }


def test_rejects_a_record_without_embedding_text():
    try:
        to_vector_document({"id": "event-123", "language": "en", "title": "Title", "content": ""})
    except ValueError as error:
        assert str(error) == "record field 'content' must be a non-empty string"
    else:
        raise AssertionError("expected invalid records to be rejected")


def test_omits_empty_ticker_metadata_for_s3_vectors_compatibility():
    document = to_vector_document(
        {"id": "event-123", "language": "en", "title": "Title", "content": "Content", "tickers": []}
    )

    assert "tickers" not in document.metadata
