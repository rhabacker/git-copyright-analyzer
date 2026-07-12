# SPDX-FileCopyrightText: 2026 Ralf Habacker <ralf.habacker@freenet.de>
#
# SPDX-License-Identifier: GPL-2.0-or-later

from __future__ import annotations

import re

from .models import HeaderEntry, HeaderRecord


class HeaderParser:
    """Extract SPDX license identifiers and copyright statements."""

    LICENSE_RE = re.compile(
        r"SPDX-License-Identifier:\s*(.+)$",
        re.IGNORECASE,
    )

    SPDX_COPYRIGHT_RE = re.compile(
        r"SPDX-FileCopyrightText:\s*(.+)$",
        re.IGNORECASE,
    )

    COPYRIGHT_RE = re.compile(
        r"Copyright\s*(?:\(C\)|©)?\s*(.+)$",
        re.IGNORECASE,
    )

    COMMENT_PREFIX = re.compile(r"^\s*(?:#|//|\*|/\*+|\*/|--|;|%)\s?")

    def parse(self, text: str) -> HeaderRecord | None:
        record = HeaderRecord()

        raw = []

        for lineno, line in enumerate(text.splitlines(), start=1):
            raw.append(line)

            normalized = self.COMMENT_PREFIX.sub("", line).strip()

            if not normalized:
                continue

            m = self.LICENSE_RE.match(normalized)
            if m:
                record.entries.append(
                    HeaderEntry(
                        line=lineno,
                        kind="license",
                        value=m.group(1).strip(),
                    )
                )
                continue

            m = self.SPDX_COPYRIGHT_RE.match(normalized)
            if m:
                record.entries.append(
                    HeaderEntry(
                        line=lineno,
                        kind="copyright",
                        value=m.group(1).strip(),
                    )
                )
                continue

            m = self.COPYRIGHT_RE.match(normalized)
            if m:
                record.entries.append(
                    HeaderEntry(
                        line=lineno,
                        kind="copyright",
                        value=m.group(1).strip(),
                    )
                )

        if not record.entries:
            return None

        record.raw_header = "\n".join(raw)
        return record
