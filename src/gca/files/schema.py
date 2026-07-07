# SPDX-FileCopyrightText: 2026 Ralf Habacker <ralf.habacker@freenet.de>
#
# SPDX-License-Identifier: GPL-2.0-or-later

FILES_SCHEMA = """
CREATE TABLE files (
    id INTEGER PRIMARY KEY,
    path TEXT UNIQUE,
    last_commit TEXT
);

CREATE VIEW file_stats AS
SELECT
    f.id,
    f.path,
    COUNT(*) AS revisions,
    SUM(ch.additions) AS additions,
    SUM(ch.deletions) AS deletions
FROM files f
JOIN changes ch
  ON ch.file_id = f.id
GROUP BY f.id;

CREATE VIEW author_file_stats AS
SELECT
    f.id AS file_id,
    f.path,
    c.author,
    COUNT(*) AS commits,
    SUM(ch.additions) AS additions,
    SUM(ch.deletions) AS deletions
FROM changes ch
JOIN commits c
  ON c.hash = ch.commit_hash
JOIN files f
  ON f.id = ch.file_id
GROUP BY
    f.id,
    c.author;
"""
