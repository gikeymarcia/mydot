#!/usr/bin/env python3
# Mikey Garcia, @gikeymarcia
# https://github.com/gikeymarcia/mydot

# https://docs.python.org/3/library/functools.html?highlight=functools#functools.cached_property
from functools import cached_property
from pathlib import Path
from typing import Union
import subprocess as sp
from os import getenv


class Dotfiles:
    def __init__(
        self,
        git_dir: Union[str, None] = None,
        work_tree: Union[str, None] = None,
    ):
        self.bare_repo = self._resolve_repo_location(git_dir)
        self.work_tree = Path(work_tree) if work_tree is not None else Path.home()
        self._git_base = [
            "git",
            f"--git-dir={self.bare_repo}",
            f"--work-tree={self.work_tree}",
        ]

    def _resolve_repo_location(self, path_string) -> Path:
        if path_string:
            return Path(path_string)
        else:
            if env_val := getenv("DOTFILES", default=None):
                return Path(env_val)
            else:
                raise KeyError("Could not find environment value for 'DOTFILES'")

    @cached_property
    def short_status(self):
        return sp.run(
            self._git_base + ["status", "-s"], text=True, capture_output=True
        ).stdout.rstrip()

    @cached_property
    def tracked(self):
        # TODO: try this: $ git ls-files --others --cached
        cmd = self._git_base + ["ls-tree", "--full-tree", "--full-name", "-r", "HEAD"]
        out = sp.run(cmd, text=True, capture_output=True).stdout.strip()
        lines = out.split("\n")
        tracked = [item.split("\t")[-1] for item in lines]
        return tracked

    @cached_property
    def staged_adds(self):
        lines = self.short_status.split("\n")
        return [" ".join(fp.split()[1:]) for fp in lines if fp[0] == "A"]

    @cached_property
    def list_all(self):
        adds = self.staged_adds
        tracked = self.tracked
        return sorted(adds + tracked)


# vim: foldlevel=99 :
