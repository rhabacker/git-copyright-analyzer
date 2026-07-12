# SPDX-FileCopyrightText: 2026 Ralf Habacker <ralf.habacker@freenet.de>
#
# SPDX-License-Identifier: GPL-2.0-or-later

from .gitlogparser import GitLogParser
from .gitrepository import GitRepository
from .headers.scanner import HeaderScanner
import typer

SCAN_EXCLUDED_PREFIXES = (
    "LICENSES/",
    ".git/",
)


class Scanner:
    def __init__(self, repo, database):
        self.git = GitRepository(repo)
        self.db = database
        self.headers = HeaderScanner(self.db)

    def should_scan(self, filename: str) -> bool:
        return not filename.startswith(SCAN_EXCLUDED_PREFIXES)

    def scan(self):
        for filename in self.git.ls_files():
            if not self.should_scan(filename):
                continue
            typer.echo(f"Scanning {filename}")
            self.scan_file(filename)

        self.db.commit()

    def scan_file(self, filename):
        file_id = self.db.get_or_create_file(filename)

        self.headers.scan(filename, file_id)

        proc = self.git.log(filename)

        last = None
        for record in GitLogParser(proc.stdout):
            last = record.commit
            self.db.insert_commit(record)
            self.db.insert_change(file_id, record)

        if last:
            self.db.update_last_commit(file_id, last)
