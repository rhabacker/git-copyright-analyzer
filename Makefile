# SPDX-FileCopyrightText: 2026 Ralf Habacker <ralf.habacker@freenet.de>
#
# SPDX-License-Identifier: CC0-1.0

.PHONY: format
format:
	ruff format .

.PHONY: lint
lint:
	ruff check .

.PHONY: fix
fix:
	ruff check --fix .
	ruff format .

.PHONY: test
test:
	pytest

.PHONY: reuse
reuse:
	reuse lint
