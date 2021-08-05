#!/usr/bin/env python3
# Mikey Garcia, @gikeymarcia
# https://github.com/gikeymarcia/mydot

# Standard Library
# https://docs.python.org/3/library/functools.html?highlight=functools#functools.cached_property
from functools import cached_property
from os import chdir, getenv
from pathlib import Path
from subprocess import run
from sys import exit as sys_exit
from typing import Union, List

# PyPi
from pydymenu import fzf

# Project Modules
from mydot.console import console
from mydot.exceptions import MissingRepositoryLocation


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
        # console.log(f"{self.bare_repo = }")
        # console.log(f"{self.work_tree = }")
        # console.log(f"{self._git_base = }")
        chdir(self.work_tree)

    def _resolve_repo_location(self, path_loc: Union[str, None]) -> Path:
        if path_loc is None:
            if env_val := getenv("DOTFILES", default=None):
                return Path(env_val)
            else:
                raise MissingRepositoryLocation(
                    "Could not find an environment value for 'DOTFILES'"
                )
        else:
            return Path(path_loc)

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
        run(self._git_base + ["branch", "-a"])
        console.print("\nModified Files:", style="header")
        run(self._git_base + ["status", "-s"])

    def choose_files(self) -> List[str]:
        select = fzf(self.list_all, prompt="Pick file(s) to edit: ", multi=True)
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
            run(cmd)

    def add(self) -> Union[List[str], None]:
        git = " ".join(self._git_base).strip()
        modified = self.modified
        if modified is None:
            sys_exit("Clean work tree. No unstaged changes present.")
        else:
            adding = fzf(
                modified,
                prompt="Choose changes to add: ",
                multi=True,
                preview=f"{git} diff --color --minimal HEAD -- " + "{}",
            )
        if adding is None:
            sys_exit("No selection made. No files will be staged.")
        else:
            cmd = self._git_base + ["add", "-v", "--"] + adding
            run(cmd)
            return adding

    @cached_property
    def editor(self) -> str:
        """Return the name of the environment defined $EDITOR."""
        return getenv("EDITOR", "vim")

    @cached_property
    def short_status(self) -> str:
        return run(
            self._git_base + ["status", "-s"], text=True, capture_output=True
        ).stdout.rstrip()

    @cached_property
    def tracked(self) -> List[str]:
        # TODO: try this: $ git ls-files --others --cached
        cmd = self._git_base + ["ls-tree", "--full-tree", "--full-name", "-r", "HEAD"]
        out = run(cmd, text=True, capture_output=True).stdout.strip()
        lines = out.split("\n")
        tracked = [item.split("\t")[-1] for item in lines]
        return tracked

    @cached_property
    def staged_adds(self) -> List[str]:
        lines = self.short_status.split("\n")
        return [" ".join(fp.split()[1:]) for fp in lines if fp[0] == "A"]

    @cached_property
    def list_all(self) -> List[str]:
        adds = self.staged_adds
        tracked = self.tracked
        return sorted(adds + tracked)

    @cached_property
    def modified(self) -> Union[List[str], None]:
        # TODO: return None when no files are modified
        mods = self._git_base + ["ls-files", "--modified"]
        proc = run(mods, capture_output=True, text=True)
        if proc.returncode == 0:
            return proc.stdout.strip().split("\n")
        else:
            return None
        sys_exit("stopping")
        return [l.split()[1] for l in self.short_status.split("\n")]


# vim: foldlevel=5 :
