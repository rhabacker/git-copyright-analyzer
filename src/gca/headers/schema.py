# SPDX-FileCopyrightText: 2026 Ralf Habacker <ralf.habacker@freenet.de>
#
# SPDX-License-Identifier: GPL-2.0-or-later

HEADER_SCHEMA = """
CREATE TABLE header_entries (
    file_id INTEGER NOT NULL,
    line INTEGER NOT NULL,
    kind TEXT NOT NULL,
    value TEXT NOT NULL
);

CREATE UNIQUE INDEX header_entries_unique
ON header_entries(file_id, line, kind, value);

CREATE VIEW header_summary AS
SELECT
    f.id,
    f.path,

    EXISTS (
        SELECT 1
        FROM header_entries h
        WHERE h.file_id = f.id
          AND h.kind = 'copyright'
    ) AS has_copyright,

    EXISTS (
        SELECT 1
        FROM header_entries h
        WHERE h.file_id = f.id
          AND h.kind = 'license'
    ) AS has_license

FROM files f;

CREATE VIEW headers AS
SELECT
    f.path,
    h.line,
    h.kind,
    h.value
FROM header_entries h
JOIN files f
  ON f.id = h.file_id
ORDER BY
    f.path,
    h.line;
"""
