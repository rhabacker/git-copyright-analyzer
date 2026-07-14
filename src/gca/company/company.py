# SPDX-FileCopyrightText: 2026 Ralf Habacker <ralf.habacker@freenet.de>
#
# SPDX-License-Identifier: GPL-2.0-or-later


def suggested_company_id(domain: str) -> str:
    """Return a suggested company id for a domain."""

    return domain.split(".", 1)[0].lower()
