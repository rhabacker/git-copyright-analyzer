# SPDX-FileCopyrightText: 2026 Ralf Habacker <ralf.habacker@freenet.de>
#
# SPDX-License-Identifier: GPL-2.0-or-later

import subprocess


class GitHistory:
    def __init__(self, repository):
        self.repository = repository

    def commits(self):
        proc = subprocess.Popen(
            [
                "git",
                "-C",
                self.repository,
                "rev-list",
                "--all",
            ],
            stdout=subprocess.PIPE,
            text=True,
        )

        for line in proc.stdout:
            yield line.strip()
