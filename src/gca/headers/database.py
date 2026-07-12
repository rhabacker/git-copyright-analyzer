# SPDX-FileCopyrightText: 2026 Ralf Habacker <ralf.habacker@freenet.de>
#
# SPDX-License-Identifier: GPL-2.0-or-later


class HeaderDatabase:
    def __init__(self, db):
        self.db = db

    def store(self, file_id, record):
        self.db.execute(
            """
            DELETE FROM header_entries
            WHERE file_id=?
            """,
            (file_id,),
        )

        for entry in record.entries:
            self.db.execute(
                """
                INSERT INTO header_entries(
                    file_id,
                    line,
                    kind,
                    value
                )
                VALUES (?, ?, ?, ?)
                """,
                (
                    file_id,
                    entry.line,
                    entry.kind,
                    entry.value,
                ),
            )
