# SPDX-FileCopyrightText: 2026 Ralf Habacker <ralf.habacker@freenet.de>
#
# SPDX-License-Identifier: GPL-2.0-or-later

from dataclasses import dataclass, field


@dataclass(slots=True)
class HeaderEntry:
    line: int
    kind: str
    value: str


@dataclass(slots=True)
class HeaderRecord:
    entries: list[HeaderEntry] = field(default_factory=list)
    raw_header: str = ""
