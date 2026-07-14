# SPDX-FileCopyrightText: 2026 Ralf Habacker <ralf.habacker@freenet.de>
#
# SPDX-License-Identifier: GPL-2.0-or-later

from __future__ import annotations

PERSONAL_PROVIDERS = {
    "gmail.com",
    "hotmail.com",
    "outlook.com",
    "live.com",
    "gmx.de",
    "gmx.com",
    "icloud.com",
    "yahoo.com",
    "protonmail.com",
    "pm.me",
}


def recommendation(
    *,
    domain: str,
    commits: int,
    authors: int,
    status: str,
) -> str:
    if status != "unknown":
        return "-"

    if domain in PERSONAL_PROVIDERS:
        return "add personal"

    if authors >= 2:
        return "add company"

    return ""
