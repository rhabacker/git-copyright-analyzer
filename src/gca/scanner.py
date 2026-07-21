# SPDX-FileCopyrightText: 2026 Ralf Habacker <ralf.habacker@freenet.de>
#
# SPDX-License-Identifier: GPL-2.0-or-later

from .gitrepository import GitRepository
from .gitcommitparser import GitCommitParser
from .headers.scanner import HeaderScanner
from .timing import timed_phase

import typer

SCAN_EXCLUDED_PREFIXES = (
    "LICENSES/",
    ".git/",
)

class Scanner:
    def __init__(self, repo, database):
        self.db = database
        self.git = GitRepository(repo)
        self.headers = HeaderScanner(self.db)

    def should_scan(self, filename: str) -> bool:
        return not filename.startswith(SCAN_EXCLUDED_PREFIXES)

    def scan(self):
        with timed_phase("Git history import"):
            self.scan_history()

        with timed_phase("Header scanning"):
            self.scan_headers()

        with timed_phase("Database commit"):
            self.db.commit()

    def scan_history(self):

        commits = 0
        changes = 0
        proc = self.git.log_all()

        for commit in GitCommitParser(proc.stdout):

            commits += 1

            if self.db.has_commit(commit.hash):
                continue

            #print(f"Scanning {commit.hash}")
            self.db.insert_commit(commit)

            for parent in commit.parents:
                self.db.insert_commit_parent(commit.hash, parent)

            for change in commit.changes:
                changes += 1
                self.db.insert_change(change)

        typer.echo(
            f"History: {commits} commits, "
            f"{changes} changes"
        )

    def scan_headers(self):
        for filename in self.git.ls_files():
            if not self.should_scan(filename):
                continue

            file_id = self.db.get_or_create_file(filename)

            #print(f"Scanning header in {filename}")
            self.headers.scan(filename, file_id)
