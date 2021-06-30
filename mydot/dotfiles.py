#!/usr/bin/env python3
# Mikey Garcia, @gikeymarcia
# https://github.com/gikeymarcia/mydot

# Standard Library
# https://docs.python.org/3/library/functools.html?highlight=functools#functools.cached_property
from functools import cached_property
from os import chdir, getenv
from pathlib import Path
import subprocess as sp
from sys import exit as sys_exit
from typing import Union

# PyPi
from pydymenu import fzf

# Project Modules
from mydot.console import console


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
        chdir(self.work_tree)

    def _resolve_repo_location(self, path_string) -> Path:
        if path_string:
            return Path(path_string)
        else:
            if env_val := getenv("DOTFILES", default=None):
                return Path(env_val)
            else:
                raise KeyError("Could not find environment value for 'DOTFILES'")

    def show_status(self) -> None:
        """Short pretty formatted info on current repo."""
        console.print("Branches:", style="header")
        sp.run(self._git_base + ["branch", "-a"])
        console.print("\nModified Files:", style="header")
        sp.run(self._git_base + ["status", "-s"])

    def choose_files(self) -> list[str]:
        all_dfs = self.list_all
        select = fzf(all_dfs, prompt="Pick file(s) to edit: ", multi=True)
        if select is None:
            sys_exit("No selection made. Cancelling action.")
        elif type(select) is str:
            raise ValueError
        else:
            return select

    def edit_files(self) -> None:
        """Interactively choose dotfiles to open in text editor.

        Searches for $EDITOR environment variable
        If not found; defaults to vim
        """
        if edits := self.choose_files():
            if len(edits) <= 1:
                cmd = [self.editor, edits[0]]
            else:
                cmd = [self.editor, "-o"] + edits
            console.log(edits, log_locals=True)
            sp.run(cmd)

    @cached_property
    def editor(self) -> str:
        """Return the name of the environment defined $EDITOR."""
        return getenv("EDITOR", "vim")

    @cached_property
    def short_status(self) -> str:
        return sp.run(
            self._git_base + ["status", "-s"], text=True, capture_output=True
        ).stdout.rstrip()

    @cached_property
    def tracked(self) -> list[str]:
        # TODO: try this: $ git ls-files --others --cached
        cmd = self._git_base + ["ls-tree", "--full-tree", "--full-name", "-r", "HEAD"]
        out = sp.run(cmd, text=True, capture_output=True).stdout.strip()
        lines = out.split("\n")
        tracked = [item.split("\t")[-1] for item in lines]
        return tracked

    @cached_property
    def staged_adds(self) -> list[str]:
        lines = self.short_status.split("\n")
        return [" ".join(fp.split()[1:]) for fp in lines if fp[0] == "A"]

    @cached_property
    def list_all(self) -> list[str]:
        adds = self.staged_adds
        tracked = self.tracked
        return sorted(adds + tracked)


# vim: foldlevel=5 :
