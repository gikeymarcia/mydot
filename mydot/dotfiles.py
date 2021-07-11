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
        self.work_tree = self._resolve_work_tree_location(work_tree)
        self._git_base = [
            "git",
            f"--git-dir={self.bare_repo}",
            f"--work-tree={self.work_tree}",
        ]
        console.log(f"{self.bare_repo = }")
        console.log(f"{self.work_tree = }")
        console.log(f"{self._git_base = }")
        chdir(self.work_tree)

    def _resolve_repo_location(self, path_loc: Union[str, None]) -> Path:
        if path_loc:
            return Path(path_loc)
        else:
            if env_val := getenv("DOTFILES", default=None):
                return Path(env_val)
            else:
                raise KeyError("Could not find environment value for 'DOTFILES'")

    @staticmethod
    def _resolve_work_tree_location(work_tree_str: Union[str, None]) -> Path:
        if work_tree_str is None:
            return Path.home()
        else:
            work_tree = Path(work_tree_str)
            if work_tree.is_dir():
                return work_tree
            else:
                raise OSError(
                    "Missing work-tree directory!\n" f"{work_tree} doesn't exist"
                )

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

    def add(self) -> Union[list[str], None]:
        adding = fzf(self.list_all, prompt="Choose changes to add: ", multi=True)
        if adding:
            return [adding] if type(adding) is str else adding

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
