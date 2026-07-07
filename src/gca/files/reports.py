# SPDX-FileCopyrightText: 2026 Ralf Habacker <ralf.habacker@freenet.de>
#
# SPDX-License-Identifier: GPL-2.0-or-later


class FilesReports:
    def __init__(self, db):
        self.db = db

    def files(self, limit=20):
        return self.db.rows(
            """
            SELECT *
            FROM file_stats
            ORDER BY revisions DESC
            LIMIT ?
        """,
            (limit,),
        )

    def contributors(self, filename):
        return self.db.rows(
            """
            SELECT
                author,
                commits,
                additions,
                deletions
            FROM author_file_stats
            WHERE path = ?
            ORDER BY additions DESC
        """,
            (filename,),
        )
