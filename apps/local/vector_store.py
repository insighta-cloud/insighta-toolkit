"""Small, file-backed vector store for the local Strands application."""

from __future__ import annotations

import json
import sqlite3
from collections.abc import Mapping, Sequence
from pathlib import Path
from typing import Any

import sqlite_vec

from insighta_toolkit.vector_documents import to_vector_document


class LocalVectorStore:
    """Persist Insighta records and embeddings in one SQLite database file."""

    def __init__(self, path: Path, *, dimensions: int) -> None:
        if dimensions < 1:
            raise ValueError("dimensions must be positive")
        path.parent.mkdir(parents=True, exist_ok=True)
        # Strands may execute a tool on a worker thread, while the store is
        # initialized on the main thread. SQLite serializes access per
        # connection; allow those read-only tool calls to share it.
        self.connection = sqlite3.connect(path, check_same_thread=False)
        self.connection.enable_load_extension(True)
        sqlite_vec.load(self.connection)
        self.connection.enable_load_extension(False)
        self.connection.execute("PRAGMA journal_mode = WAL")
        self.connection.execute(
            "CREATE TABLE IF NOT EXISTS settings (key TEXT PRIMARY KEY, value TEXT NOT NULL)"
        )
        existing = self.connection.execute(
            "SELECT value FROM settings WHERE key = 'dimensions'"
        ).fetchone()
        if existing is None:
            self.connection.execute(
                "INSERT INTO settings (key, value) VALUES ('dimensions', ?)", (str(dimensions),)
            )
            self.connection.execute(
                "CREATE VIRTUAL TABLE vectors USING vec0("
                f"embedding float[{dimensions}] distance_metric=cosine, +key TEXT)"
            )
        elif int(existing[0]) != dimensions:
            raise ValueError(
                f"database has {existing[0]} dimensions; rebuild it for "
                f"{dimensions}-dimension embeddings"
            )
        self.connection.execute(
            "CREATE TABLE IF NOT EXISTS records (key TEXT PRIMARY KEY, record_json TEXT NOT NULL, "
            "language TEXT NOT NULL, tickers_json TEXT NOT NULL)"
        )
        self.connection.commit()
        self.dimensions = dimensions

    def close(self) -> None:
        self.connection.close()

    def upsert(self, record: Mapping[str, Any], embedding: Sequence[float]) -> None:
        """Add or replace a record and its normalized embedding."""

        if len(embedding) != self.dimensions:
            raise ValueError(f"embedding must have {self.dimensions} dimensions")
        document = to_vector_document(record)
        self.connection.execute(
            "INSERT OR REPLACE INTO records "
            "(key, record_json, language, tickers_json) VALUES (?, ?, ?, ?)",
            (
                document.key,
                json.dumps(dict(record), ensure_ascii=False),
                document.metadata["language"],
                json.dumps([ticker.upper() for ticker in document.metadata.get("tickers", [])]),
            ),
        )
        self.connection.execute("DELETE FROM vectors WHERE key = ?", (document.key,))
        self.connection.execute(
            "INSERT INTO vectors (embedding, key) VALUES (?, ?)",
            (sqlite_vec.serialize_float32(list(embedding)), document.key),
        )
        self.connection.commit()

    def search(
        self,
        embedding: Sequence[float],
        *,
        language: str | None = None,
        ticker: str | None = None,
        top_k: int = 5,
    ) -> list[dict[str, Any]]:
        """Return nearest source records, optionally filtered by language or ticker."""

        if len(embedding) != self.dimensions:
            raise ValueError(f"embedding must have {self.dimensions} dimensions")
        if not 1 <= top_k <= 10:
            raise ValueError("top_k must be between 1 and 10")
        rows = self.connection.execute(
            "SELECT key, distance FROM vectors WHERE embedding MATCH ? AND k = ?",
            (sqlite_vec.serialize_float32(list(embedding)), top_k * 10),
        ).fetchall()
        results: list[dict[str, Any]] = []
        for key, distance in rows:
            row = self.connection.execute(
                "SELECT record_json, language, tickers_json FROM records WHERE key = ?", (key,)
            ).fetchone()
            if row is None or (language and row[1] != language):
                continue
            if ticker and ticker.upper() not in json.loads(row[2]):
                continue
            results.append({"record": json.loads(row[0]), "distance": distance})
            if len(results) == top_k:
                break
        return results
