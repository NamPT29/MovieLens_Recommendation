from __future__ import annotations

from dataclasses import dataclass
from functools import lru_cache
import os
from typing import Dict, Optional


@dataclass(frozen=True)
class MySQLConfig:
    host: str
    port: int
    user: str
    password: str
    database: str

    def as_dict(self) -> Dict[str, object]:
        return {
            "host": self.host,
            "port": self.port,
            "user": self.user,
            "password": self.password,
            "database": self.database,
        }


@lru_cache
def get_mysql_config() -> Optional[MySQLConfig]:
    """Load MySQL connection info from environment variables."""
    required_vars = [
        "MYSQL_HOST",
        "MYSQL_PORT",
        "MYSQL_USER",
        "MYSQL_PASSWORD",
        "MYSQL_DATABASE",
    ]
    if any(os.getenv(var) is None for var in required_vars):
        return None

    try:
        port = int(os.getenv("MYSQL_PORT", "3306"))
    except ValueError:
        port = 3306

    return MySQLConfig(
        host=os.getenv("MYSQL_HOST", "localhost"),
        port=port,
        user=os.getenv("MYSQL_USER", "root"),
        password=os.getenv("MYSQL_PASSWORD", "MatKhauMoi123!"),
        database=os.getenv("MYSQL_DATABASE", "movielens"),
    )


def mysql_is_configured() -> bool:
    return get_mysql_config() is not None
