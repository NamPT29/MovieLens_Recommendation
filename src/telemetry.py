from __future__ import annotations

from typing import Iterable, Optional, TYPE_CHECKING

try:
    from mysql.connector import pooling
    MYSQL_DRIVER_AVAILABLE = True
except ModuleNotFoundError:
    pooling = None  # type: ignore[assignment]
    MYSQL_DRIVER_AVAILABLE = False

if TYPE_CHECKING:
    from mysql.connector.pooling import MySQLConnectionPool
else:
    MySQLConnectionPool = object

import pandas as pd

from src.config import get_mysql_config, mysql_is_configured

_connection_pool: Optional[MySQLConnectionPool] = None


def _get_pool() -> MySQLConnectionPool:
    global _connection_pool
    if not MYSQL_DRIVER_AVAILABLE:
        raise RuntimeError(
            "Chưa cài mysql-connector-python. Chạy 'pip install mysql-connector-python' để bật telemetry."
        )
    config = get_mysql_config()
    if config is None:
        raise RuntimeError("MySQL chưa được cấu hình. Thiết lập biến môi trường trước khi log.")

    if _connection_pool is None:
        _connection_pool = pooling.MySQLConnectionPool(
            pool_name="recommender_pool",
            pool_size=5,
            **config.as_dict(),
        )
    return _connection_pool


def log_recommendations(
    user_id: int,
    model_name: str,
    recommendations: pd.DataFrame,
    action: str = "view",
) -> int:
    """Lưu danh sách gợi ý đã hiển thị vào bảng user_interactions."""
    if not MYSQL_DRIVER_AVAILABLE or not mysql_is_configured() or recommendations.empty:
        return 0

    rows: list[tuple] = []
    for row in recommendations.itertuples():
        movie_id = getattr(row, "movieId", None)
        if movie_id is None:
            continue
        score = getattr(row, "model_score", None)
        rows.append((int(user_id), str(model_name), int(movie_id), action, score))

    if not rows:
        return 0

    pool = _get_pool()
    connection = pool.get_connection()
    inserted = 0
    try:
        cursor = connection.cursor()
        cursor.executemany(
            """
            INSERT INTO user_interactions
                (user_id, model_used, movie_id, action, score_shown)
            VALUES (%s, %s, %s, %s, %s)
            """,
            rows,
        )
        connection.commit()
        inserted = cursor.rowcount or 0
    finally:
        cursor.close()
        connection.close()
    return inserted


def fetch_recent_logs(limit: int = 20) -> Iterable[dict]:
    if not MYSQL_DRIVER_AVAILABLE or not mysql_is_configured():
        return []
    pool = _get_pool()
    connection = pool.get_connection()
    try:
        cursor = connection.cursor(dictionary=True)
        cursor.execute(
            """
            SELECT user_id, model_used, movie_id, action, score_shown, created_at
            FROM user_interactions
            ORDER BY created_at DESC
            LIMIT %s
            """,
            (limit,),
        )
        return cursor.fetchall()
    finally:
        cursor.close()
        connection.close()


def telemetry_available() -> bool:
    return MYSQL_DRIVER_AVAILABLE and mysql_is_configured()
