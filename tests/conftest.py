import os
import sys
import tempfile

import pytest

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from app import db  # noqa: E402
from migrations import runner  # noqa: E402


@pytest.fixture
def db_path(tmp_path):
    path = str(tmp_path / "taskflow_test.db")
    conn = db.get_connection(path)
    runner.migrate_up(conn)
    conn.close()
    return path


@pytest.fixture
def conn(db_path):
    c = db.get_connection(db_path)
    yield c
    c.close()
