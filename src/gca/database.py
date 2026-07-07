# SPDX-FileCopyrightText: 2026 Ralf Habacker <ralf.habacker@freenet.de>
#
# SPDX-License-Identifier: GPL-2.0-or-later

import sqlite3

from .schema import SCHEMA, SCHEMA_VERSION


class Database:
    def __init__(self, filename):
        self.db = sqlite3.connect(filename)
        self.db.row_factory = sqlite3.Row

    def initialize(self):
        self.db.executescript(SCHEMA)

        self.db.execute(
            """
            INSERT OR REPLACE INTO metadata(key, value)
            VALUES (?, ?)
        """,
            ("schema_version", str(SCHEMA_VERSION)),
        )

        self.db.commit()

    def execute(self, sql, args=()):
        return self.db.execute(sql, args)

    def commit(self):
        self.db.commit()

    def schema_version(self):
        try:
            row = self.db.execute("""
                SELECT value
                FROM metadata
                WHERE key='schema_version'
            """).fetchone()
        except sqlite3.OperationalError:
            # Fresh database: schema has not been initialized yet.
            return None

        if row is None:
            return None

        return int(row[0])

    def check_version(self):
        version = self.schema_version()

        if version != SCHEMA_VERSION:
            raise RuntimeError(
                f"Database schema {version} is not supported "
                f"(expected {SCHEMA_VERSION}). "
                "Please recreate the database with 'gca init'."
            )

    def get_setting(self, key: str) -> str | None:
        row = self.execute(
            "SELECT value FROM settings WHERE key = ?",
            (key,),
        ).fetchone()

        return None if row is None else row["value"]

    def set_setting(self, key: str, value: str) -> None:
        self.execute(
            """
            INSERT INTO settings(key, value)
            VALUES (?, ?)
            ON CONFLICT(key)
            DO UPDATE SET value = excluded.value
            """,
            (key, value),
        )

    def get_or_create_file(self, path):
        row = self.execute(
            "SELECT id FROM files WHERE path=?",
            (path,),
        ).fetchone()

        if row:
            return row[0]

        cursor = self.execute(
            """
            INSERT INTO files(path)
            VALUES (?)
            """,
            (path,),
        )

        return cursor.lastrowid

    def insert_commit(self, record):
        self.execute(
            """
            INSERT OR IGNORE INTO commits(
                hash,
                author,
                email,
                date,
                subject
            )
            VALUES (?, ?, ?, ?, ?)
            """,
            (
                record.commit,
                record.author,
                record.email,
                record.timestamp,
                record.subject,
            ),
        )

    def insert_change(self, file_id, record):
        self.execute(
            """
            INSERT OR IGNORE INTO changes(
                file_id,
                commit_hash,
                additions,
                deletions,
                patch
            )
            VALUES (?, ?, ?, ?, ?)
            """,
            (
                file_id,
                record.commit,
                record.additions,
                record.deletions,
                record.patch,
            ),
        )

    def update_last_commit(self, file_id, commit):
        self.execute(
            """
            UPDATE files
            SET last_commit=?
            WHERE id=?
            """,
            (
                commit,
                file_id,
            ),
        )

    def rows(self, sql, args=()):
        return self.execute(sql, args).fetchall()

    def scalar(self, sql, args=()):
        row = self.db.execute(sql, args).fetchone()
        return row[0] if row else 0

    def file_count(self):
        return self.scalar("SELECT COUNT(*) FROM files")

    def commit_count(self):
        return self.scalar("SELECT COUNT(*) FROM commits")

    def change_count(self):
        return self.scalar("SELECT COUNT(*) FROM changes")

    def author_count(self):
        return self.scalar(
            """
            SELECT COUNT(DISTINCT author)
            FROM commits
        """
        )
