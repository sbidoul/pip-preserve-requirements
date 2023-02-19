# SPDX-FileCopyrightText: 2023-present Stéphane Bidoul <stephane.bidoul@gmail.com>
# SPDX-License-Identifier: MIT

from pathlib import Path
from typing import Sequence
import sqlite3


class Cache:
    def __init__(self, project_root: Path):
        self._cache_dir = project_root / ".pip_preserve_requirements_cache"
        self._tags_db_conn = self._initialize()

    def _initialize(self) -> sqlite3.Connection:
        if not self._cache_dir.is_dir():
            self._cache_dir.mkdir()
        gitignore_path = self._cache_dir / ".gitignore"
        if not gitignore_path.is_file():
            gitignore_path.write_text("*")
        cachedir_tag_path = self._cache_dir / "CACHEDIR.TAG"
        if not cachedir_tag_path.is_file():
            cachedir_tag_path.write_text("Signature: 8a477f597d28d172789f06886806bc55")
        tags_db_path = self._cache_dir / "tags.db"
        conn = sqlite3.connect(tags_db_path, isolation_level=None)
        conn.execute(
            """
                CREATE TABLE IF NOT EXISTS tags (
                    provider TEXT NOT NULL,
                    owner TEXT NOT NULL,
                    repo TEXT NOT NULL,
                    sha TEXT NOT NULL,
                    tag TEXT NOT NULL
                );
            """
        )
        return conn

    def get_commit_tags(
        self, provider: str, owner: str, repo: str, sha: str
    ) -> Sequence[str]:
        query = (
            "SELECT tag FROM tags WHERE "
            "provider = ? AND owner = ? AND repo = ? AND sha = ?"
        )
        params = [provider, owner, repo, sha]
        return [tag for (tag,) in self._tags_db_conn.execute(query, params).fetchall()]

    def add_commit_tag(
        self, provider: str, owner: str, repo: str, sha: str, tag: str
    ) -> None:
        query = (
            "INSERT INTO tags (provider, owner, repo, sha, tag) VALUES (?, ?, ?, ?, ?)"
        )
        params = [provider, owner, repo, sha, tag]
        self._tags_db_conn.execute(query, params)

    def remove_commit_tags(
        self, provider: str, owner: str, repo: str, sha: str
    ) -> None:
        query = (
            "DELETE FROM tags WHERE "
            "provider = ? AND owner = ? AND repo = ? AND sha = ?"
        )
        params = [provider, owner, repo, sha]
        self._tags_db_conn.execute(query, params)

    def update_commit_tags(
        self, provider: str, owner: str, repo: str, sha: str, tags: Sequence[str]
    ) -> None:
        self.remove_commit_tags(provider, owner, repo, sha)
        for tag in tags:
            self.add_commit_tag(provider, owner, repo, sha, tag)
