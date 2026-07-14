# SPDX-FileCopyrightText: 2026 Ralf Habacker <ralf.habacker@freenet.de>
#
# SPDX-License-Identifier: GPL-2.0-or-later

from dataclasses import dataclass, field


@dataclass
class AuthorCompany:
    author_id: int
    company_id: int
    confidence: int
    source: str
    evidence: str


@dataclass(slots=True)
class Company:
    id: str
    name: str
    spdx_name: str | None
    domains: list[str]


@dataclass(slots=True)
class CompanyDefinition:
    """Company definition loaded from YAML."""

    id: str
    name: str
    spdx_name: str
    domains: list[str] = field(default_factory=list)


@dataclass
class MappingResult:
    authors: int
    mapped: int
    skipped: int
