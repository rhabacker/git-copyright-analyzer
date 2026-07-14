# SPDX-FileCopyrightText: 2026 Ralf Habacker <ralf.habacker@freenet.de>
#
# SPDX-License-Identifier: GPL-2.0-or-later

from __future__ import annotations

from collections.abc import Iterator
from importlib.resources import files
from pathlib import Path

import yaml

from .models import CompanyDefinition


class CompanyConfig:
    def __init__(self) -> None:
        self._companies: dict[str, CompanyDefinition] = {}
        self._domains: dict[str, CompanyDefinition] = {}
        self._personal_domains: set[str] = set()

    @classmethod
    def load(cls, repository: Path | None = None) -> "CompanyConfig":
        cfg = cls()

        cfg._load_yaml(files(__package__).joinpath("builtin.yaml"))

        if repository is not None:
            local = repository / ".gca" / "company.yaml"
            if local.exists():
                cfg._load_yaml(local)

        return cfg

    def company_for_domain(self, domain: str) -> CompanyDefinition | None:
        return self._domains.get(domain.lower())

    def companies(self) -> Iterator[tuple[str, CompanyDefinition]]:
        return self._companies.values()

    def domains(self) -> Iterator[tuple[str, CompanyDefinition]]:
        return self._domains.items()

    def personal_domains(self) -> set[str]:
        return self._personal_domains

    def iter_personal_domains(self) -> Iterator[str]:
        return iter(sorted(self._personal_domains))

    def _load_yaml(self, filename: Path) -> None:
        with filename.open("r", encoding="utf-8") as fp:
            data = yaml.safe_load(fp) or {}

        for entry in data.get("companies", []):
            company_id = entry.get("id")
            if not company_id:
                raise ValueError(f"Missing company id: {entry}")

            name = entry.get("name")
            if not name:
                raise ValueError(f"Company '{company_id}' is missing 'name'")

            domains = entry.get("domains")
            if not domains:
                raise ValueError(f"Company '{company_id}' has no domains")

            company = CompanyDefinition(
                id=entry["id"],
                name=entry["name"],
                spdx_name=entry.get("spdx_name", entry["name"]),
                domains=list(entry.get("domains", [])),
            )

            self._companies[company.name] = company

            for domain in company.domains:
                self._domains[domain.lower()] = company

        for domain in data.get("personal_domains", []):
            self._personal_domains.add(domain.lower())
