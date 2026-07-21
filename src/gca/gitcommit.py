# SPDX-FileCopyrightText: 2026 Ralf Habacker <ralf.habacker@freenet.de>
#
# SPDX-License-Identifier: GPL-2.0-or-later

from dataclasses import dataclass, field


@dataclass
class GitChange:
    commit_hash: str
    path: str
    additions: int
    deletions: int
    patch: str | None = None


@dataclass
class GitCommit:
    hash: str
    author: str
    email: str
    timestamp: int
    subject: str

    parents: list[str] = field(default_factory=list)
    changes: list[GitChange] = field(default_factory=list)
