# SPDX-FileCopyrightText: 2026 Ralf Habacker <ralf.habacker@freenet.de>
#
# SPDX-License-Identifier: GPL-2.0-or-later

from dataclasses import dataclass


@dataclass(slots=True)
class CommitRecord:
    commit: str
    author: str
    email: str
    timestamp: int
    subject: str
    additions: int = 0
    deletions: int = 0
    patch: str = ""

    def add_numstat(self, cols: list[str]) -> bool:
        if len(cols) != 3:
            return False

        if cols[0] == "-" or cols[1] == "-":
            return True  # binary file

        try:
            self.additions += int(cols[0])
            self.deletions += int(cols[1])
        except ValueError:
            return False

        return True

    def finish(self, patch_lines: list[str]) -> None:
        self.patch = "".join(patch_lines)


@dataclass
class HistoryStatistics:
    commits_scanned: int = 0
    commits_imported: int = 0
    changes_imported: int = 0
    parents_imported: int = 0
    elapsed: float = 0.0


@dataclass
class HeaderStatistics:
    files_ignored: int = 0
    files_scanned: int = 0
    headers_found: int = 0
    spdx_headers: int = 0
    elapsed: float = 0.0


@dataclass
class ScanStatistics:
    history: HistoryStatistics
    headers: HeaderStatistics
    db_commit_time: float = 0.0
    total_elapsed: float = 0.0
