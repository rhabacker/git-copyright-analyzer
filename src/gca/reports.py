# SPDX-FileCopyrightText: 2026 Ralf Habacker <ralf.habacker@freenet.de>
#
# SPDX-License-Identifier: GPL-2.0-or-later


from .files.reports import FilesReports
from .headers.reports import HeaderReports


class Reports:
    def __init__(self, db):
        self.db = db
        self.files = FilesReports(db)
        self.headers = HeaderReports(db)

    def summary(self):
        return {
            "files": self.db.scalar("SELECT COUNT(*) FROM files"),
            "commits": self.db.scalar("SELECT COUNT(*) FROM commits"),
            "authors": self.db.scalar("SELECT COUNT(*) FROM author_stats"),
            "changes": self.db.scalar("SELECT COUNT(*) FROM changes"),
        }

    def commits(self, limit=20):
        return self.db.execute(
            """
            SELECT *
            FROM commit_stats
            ORDER BY commit_hash DESC
            LIMIT ?
        """,
            (limit,),
        )

    def contributors(self):
        return self.db.execute(
            """
            SELECT *
            FROM contributor_stats
            ORDER BY commits DESC
        """
        )

    def largest_commits(self, limit=20):
        return self.db.rows(
            """
            SELECT *
            FROM commit_stats
            ORDER BY additions DESC
            LIMIT ?
        """,
            (limit,),
        )
