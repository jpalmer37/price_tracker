import os
from pathlib import Path

from scraper.database.config import get_database_url


def test_database_url_defaults_to_sqlite(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    monkeypatch.delenv("DATABASE_PATH", raising=False)

    assert get_database_url() == f"sqlite:///{tmp_path / 'price_tracker.db'}"


def test_database_url_with_custom_path_creates_parent(tmp_path, monkeypatch):
    db_path = tmp_path / "data" / "tracker.db"
    monkeypatch.setenv("DATABASE_PATH", os.fspath(db_path))

    assert get_database_url() == f"sqlite:///{db_path}"
    assert db_path.parent.is_dir()


def test_database_url_resolves_relative_paths_from_cwd(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    monkeypatch.setenv("DATABASE_PATH", "data/relative.db")

    assert get_database_url() == f"sqlite:///{tmp_path / 'data' / 'relative.db'}"
