from __future__ import annotations

import unittest
from unittest import mock

import pandas as pd

import src.telemetry as telemetry


class DummyCursor:
    def __init__(self, rows=None):
        self.statements = []
        self.rowcount = 0
        self.rows = rows or []

    def executemany(self, query, rows):
        self.statements.append((query, rows))
        self.rowcount = len(rows)

    def execute(self, query, params):
        self.statements.append((query, params))

    def fetchall(self):
        return self.rows

    def close(self):
        pass


class DummyConnection:
    def __init__(self, cursor):
        self._cursor = cursor
        self.commits = 0

    def cursor(self, dictionary=False):
        return self._cursor

    def commit(self):
        self.commits += 1

    def close(self):
        pass


class DummyPool:
    def __init__(self, cursor):
        self.connection = DummyConnection(cursor)

    def get_connection(self):
        return self.connection


class TelemetryTests(unittest.TestCase):
    def setUp(self):
        telemetry._connection_pool = None

    def test_log_recommendations_returns_zero_without_config(self):
        df = pd.DataFrame({"movieId": [1], "model_score": [4.5]})
        with mock.patch("src.telemetry.mysql_is_configured", return_value=False):
            inserted = telemetry.log_recommendations(1, "Content", df)
        self.assertEqual(inserted, 0)

    def test_log_recommendations_inserts_rows_when_configured(self):
        df = pd.DataFrame({"movieId": [1, 2], "model_score": [4.5, 3.7]})
        cursor = DummyCursor()
        pool = DummyPool(cursor)
        with mock.patch("src.telemetry.mysql_is_configured", return_value=True), (
            mock.patch("src.telemetry._get_pool", return_value=pool)
        ):
            inserted = telemetry.log_recommendations(1, "Hybrid", df)
        self.assertEqual(inserted, 2)
        self.assertEqual(cursor.rowcount, 2)

    def test_fetch_recent_logs_returns_empty_when_not_configured(self):
        with mock.patch("src.telemetry.mysql_is_configured", return_value=False):
            result = telemetry.fetch_recent_logs(limit=5)
        self.assertEqual(result, [])

    def test_fetch_recent_logs_returns_rows(self):
        rows = [
            {
                "user_id": 1,
                "model_used": "Hybrid",
                "movie_id": 10,
                "action": "auto",
                "score_shown": 4.5,
                "created_at": "2025-12-10 00:00:00",
            }
        ]
        cursor = DummyCursor(rows=rows)
        pool = DummyPool(cursor)
        with mock.patch("src.telemetry.mysql_is_configured", return_value=True), (
            mock.patch("src.telemetry._get_pool", return_value=pool)
        ):
            result = telemetry.fetch_recent_logs(limit=5)
        self.assertEqual(result, rows)


if __name__ == "__main__":
    unittest.main()
