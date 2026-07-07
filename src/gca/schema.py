# SPDX-FileCopyrightText: 2026 Ralf Habacker <ralf.habacker@freenet.de>
#
# SPDX-License-Identifier: GPL-2.0-or-later


from .files.schema import FILES_SCHEMA


SCHEMA_VERSION = 1
REPOSITORY_SCHEMA = """
CREATE TABLE changes (
    id INTEGER PRIMARY KEY,
    file_id INTEGER,
    commit_hash TEXT,
    additions INTEGER,
    deletions INTEGER,
    patch TEXT
);

CREATE TABLE commits (
    hash TEXT PRIMARY KEY,
    author TEXT,
    email TEXT,
    date INTEGER,
    subject TEXT
);

CREATE TABLE metadata (
    key TEXT PRIMARY KEY,
    value TEXT
);

CREATE TABLE settings (
    key   TEXT PRIMARY KEY,
    value TEXT NOT NULL
);

CREATE UNIQUE INDEX changes_unique
ON changes(file_id, commit_hash);

CREATE VIEW author_stats AS
SELECT
    c.author,
    COUNT(*) AS commits,
    SUM(cs.additions) AS additions,
    SUM(cs.deletions) AS deletions
FROM commits c
JOIN commit_stats cs
  ON cs.commit_hash = c.hash
GROUP BY c.author;

CREATE VIEW commit_stats AS
SELECT
    commit_hash,
    SUM(additions) AS additions,
    SUM(deletions) AS deletions,
    COUNT(*) AS files
FROM changes
GROUP BY commit_hash;

CREATE VIEW contributor_stats AS
SELECT
    a.author,
    a.commits,
    COUNT(*) AS files,
    a.additions,
    a.deletions
FROM author_stats a
JOIN author_file_stats af
  ON af.author = a.author
GROUP BY
    a.author,
    a.commits,
    a.additions,
    a.deletions;
"""

SCHEMA = "\n".join(
    [
        REPOSITORY_SCHEMA,
        FILES_SCHEMA,
    ]
)
