# SPDX-FileCopyrightText: 2026 Ralf Habacker <ralf.habacker@freenet.de>
#
# SPDX-License-Identifier: GPL-2.0-or-later

from .models import CommitRecord

RS = "\x1e"
FS = "\x1f"


class GitLogParser:
    def __init__(self, stream):
        self.stream = stream

    def _parse_header(self, line: str) -> CommitRecord:
        header = line[1:].rstrip("\n").split(FS)
        return CommitRecord(
            commit=header[0],
            author=header[1],
            email=header[2],
            timestamp=int(header[3]),
            subject=header[4],
        )

    def _finish_commit(self, current: CommitRecord, patch: list[str]) -> CommitRecord:
        current.finish(patch)
        return current

    def _parse_numstat(self, current: CommitRecord, line: str) -> bool:
        cols = line.rstrip("\n").split("\t")

        if len(cols) != 3:
            return False

        return current.add_numstat(cols)

    def __iter__(self):
        current: CommitRecord | None = None
        patch: list[str] = []

        for raw in self.stream:
            line = raw.decode("utf-8", "replace")

            if line.startswith(RS):
                if current is not None:
                    yield self._finish_commit(current, patch)

                current = self._parse_header(line)
                patch = []
                continue

            if current is None:
                continue

            if self._parse_numstat(current, line):
                continue

            patch.append(line)

        if current is not None:
            yield self._finish_commit(current, patch)
