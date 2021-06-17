#!/usr/bin/env python3
# Mikey Garcia, @gikeymarcia
# https://github.com/gikeymarcia/mydot

from pathlib import Path
import os


class Dotfiles:
    def __init__(self, git_dir=None, work_tree=None):
        self.bare_repo = self.resolve_repo_location(git_dir)
        self.work_tree = Path(work_tree) if work_tree else Path.home()

    def resolve_repo_location(self, path_string):
        if path_string:
            return Path(path_string)
        else:
            if env_val := os.getenv("DOTFILES", default=None):
                return Path(env_val)
            else:
                raise KeyError("Could not find environment value for 'DOTFILES'")
