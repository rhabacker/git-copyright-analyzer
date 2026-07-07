# SPDX-FileCopyrightText: 2026 Ralf Habacker <ralf.habacker@freenet.de>
#
# SPDX-License-Identifier: GPL-2.0-or-later

import subprocess


class GitRepository:
    def __init__(self, path):
        self.path = path

    def ls_files(self):
        out = subprocess.check_output(
            ["git", "-C", self.path, "ls-files"],
            text=True,
        )
        return out.splitlines()

    def log(self, filename):
        cmd = [
            "git",
            "-c",
            "i18n.logOutputEncoding=UTF-8",
            "-C",
            self.path,
            "log",
            "--follow",
            "--patch",
            "--numstat",
            "--date=unix",
            "--format=%x1e%H%x1f%an%x1f%ae%x1f%at%x1f%s",
            "--",
            filename,
        ]

        return subprocess.Popen(
            cmd,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
        )
