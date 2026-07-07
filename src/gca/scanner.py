# SPDX-FileCopyrightText: 2026 Ralf Habacker <ralf.habacker@freenet.de>
#
# SPDX-License-Identifier: GPL-2.0-or-later

from .gitrepository import GitRepository
from .gitlogparser import GitLogParser


class Scanner:
    def __init__(self, repo, database):
        self.git = GitRepository(repo)
        self.db = database

    def scan(self):
        for filename in self.git.ls_files():
            self.scan_file(filename)

        self.db.commit()

    def scan_file(self, filename):
        print(f"{filename}")
        file_id = self.db.get_or_create_file(filename)

        proc = self.git.log(filename)

        last = None
        for record in GitLogParser(proc.stdout):
            last = record.commit
            self.db.insert_commit(record)
            self.db.insert_change(file_id, record)

        if last:
            self.db.update_last_commit(file_id, last)
