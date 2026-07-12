# SPDX-FileCopyrightText: 2026 Ralf Habacker <ralf.habacker@freenet.de>
#
# SPDX-License-Identifier: GPL-2.0-or-later


class HeaderReports:
    def __init__(self, db):
        self.db = db

    def headers(self):
        return self.db.rows(
            """
            SELECT *
            FROM headers
        """
        )

    def missing_copyright(self):
        return self.db.rows(
            """
            SELECT path
            FROM header_summary
            WHERE NOT has_copyright
            ORDER BY path
        """
        )

    def missing_license(self):
        return self.db.rows(
            """
            SELECT path
            FROM header_summary
            WHERE NOT has_license
            ORDER BY path
        """
        )

    def missing_headers(self):
        return self.db.rows(
            """
            SELECT path
            FROM header_summary
            WHERE NOT has_copyright
              AND NOT has_license
            ORDER BY path
        """
        )
