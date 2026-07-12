# SPDX-FileCopyrightText: 2026 Ralf Habacker <ralf.habacker@freenet.de>
#
# SPDX-License-Identifier: GPL-2.0-or-later

from .parser import HeaderParser
from .database import HeaderDatabase

HEADER_LINES = 100
HEADER_BYTES = 8192


class HeaderScanner:
    def __init__(self, db):
        self.db = db

    def _read_header(self, filename):
        with open(filename, encoding="utf-8", errors="replace") as f:
            lines = []

            size = 0

            for _ in range(HEADER_LINES):
                line = f.readline()
                if not line:
                    break

                lines.append(line)
                size += len(line)

                if size >= HEADER_BYTES:
                    break

            return "".join(lines)

    def scan(self, path, file_id):
        header = self._read_header(path)
        record = HeaderParser().parse(header)
        if record:
            HeaderDatabase(self.db).store(file_id, record)
