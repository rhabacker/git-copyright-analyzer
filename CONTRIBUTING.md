<!--
SPDX-FileCopyrightText: 2026 Ralf Habacker <ralf.habacker@freenet.de>

SPDX-License-Identifier: CC0-1.0
-->

Module naming
-------------

Modules containing a primary class are named after that class converted to lowercase
(e.g. GitLogParser → gitlogparser.py, GitRepository → gitrepository.py). This avoids
ambiguity about underscore placement and makes class-to-module mapping deterministic.