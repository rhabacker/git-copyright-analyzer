# SPDX-FileCopyrightText: 2026 Ralf Habacker <ralf.habacker@freenet.de>
#
# SPDX-License-Identifier: GPL-2.0-or-later

from .repository import CompanyRepository


class CompanyMapper:
    def __init__(self, db, config):
        self.db = db
        self.repo = CompanyRepository(db)
        self.config = config

    def run(self):
        count = 0

        for author in self.repo.iter_commit_authors():
            if not author["email"]:
                continue

            _, _, domain = author["email"].lower().partition("@")

            company = self.config.company_for_domain(domain)
            if company is None:
                continue

            company_id = self.repo.company_id(company.name)
            if company_id is None:
                continue

            if self.repo.has_mapping(
                author["author"],
                author["email"],
            ):
                continue

            self.repo.set_mapping(
                author["author"],
                author["email"],
                company_id,
                source="domain",
                confidence=100,
                evidence=author["email"],
            )

            count += 1

        self.db.commit()
        return count
