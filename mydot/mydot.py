#!/usr/bin/env python3
# Mikey Garcia, @gikeymarcia
# https://github.com/gikeymarcia/mydot

from pathlib import Path
import subprocess as sp
import os


class Dotfiles:
    def __init__(self, git_dir=None, work_tree=None):
        self.bare_repo = self.resolve_repo_location(git_dir)
        self.work_tree = Path(work_tree) if work_tree else Path.home()
        self._git_base = [
            "git",
            f"--git-dir={self.bare_repo}",
            f"--work-tree={self.work_tree}",
        ]

    def get_short_status(self):
        return sp.run(
            self._git_base + ["status", "-s"], text=True, capture_output=True
        ).stdout.rstrip()

    def resolve_repo_location(self, path_string):
        if path_string:
            return Path(path_string)
        else:
            if env_val := os.getenv("DOTFILES", default=None):
                return Path(env_val)
            else:
                raise KeyError("Could not find environment value for 'DOTFILES'")

    def list(self):
        status_out = self.get_short_status()
        lines = status_out.split("\n")
        files = ["".join(fp.split()[1:]) for fp in lines]
        return files


# vim: foldlevel=99 :
