#!/usr/bin/env python3
# Mikey Garcia, @gikeymarcia
# https://github.com/gikeymarcia/mydot

# Standard Library
# https://docs.python.org/3/library/functools.html?highlight=functools#functools.cached_property
from functools import cached_property
import os
from pathlib import Path
import shutil
import subprocess
from typing import List, Union


from mydot.console import console
from mydot.exceptions import MissingRepositoryLocation, WorktreeMissing


# Custom Type
OptionalPath = Union[Path, str, None]


class Repository:
    """
    Gets git-context aware slices of data from your repository.

    Useful Methods
    .show_status() general purpose report of repository state
    .freshen() drop cached results. New data will be polled at next execution.

    Useful PROPERTIES
    .tracked -- list of files already committed in repo
    .list_all -- list of committed and staged files
    .restorables --
    """

    def __init__(
        self,
        local_bare_repo: OptionalPath = None,
        work_tree: OptionalPath = None,
    ):
        """Create a new Dotfiles object to manage your repository.

        When no locations are passed the default locations are:
        - "$DOTFILES" for the bare repository
        - "$HOME" for the work tree
        """
        self.bare_repo: Path = self._resolve_repo_location(local_bare_repo)
        self.work_tree: Path = self._resolve_work_tree_location(work_tree)
        self._git_base: List[str] = [
            "git",
            f"--git-dir={self.bare_repo}",
            f"--work-tree={self.work_tree}",
        ]
        self.run_from: Path = Path.cwd()
        os.chdir(self.work_tree)

    def show_status(self) -> None:
        """Short pretty formatted info about the repo state."""
        console.print("Branches:", style="header")
        subprocess.run(self._git_base + ["branch", "-a"])
        console.print("\nModified Files:", style="header")
        subprocess.run(self._git_base + ["status", "-s"])

    @staticmethod
    def _resolve_repo_location(path_loc: OptionalPath) -> Path:
        """Decides which dotfile repository location will be used.

        When None is given, try to read $DOTFILES from environment.
        When a location is specified return it's Path
        """
        if path_loc is None:
            if env_val := os.getenv("DOTFILES", default=None):
                return Path(env_val)
            else:
                raise MissingRepositoryLocation(
                    "No repository specified and no value for $DOTFILES in environment."
                )
        else:
            return Path(path_loc) if isinstance(path_loc, str) else path_loc

    @staticmethod
    def _resolve_work_tree_location(dir: OptionalPath) -> Path:
        """Define work tree location.

        When None given presume Path.home()
        """
        if dir is None:
            return Path.home()
        else:
            work_tree: Path = Path(dir) if isinstance(dir, str) else dir
            if work_tree.is_dir():
                return work_tree
            else:
                msg = "Missing work-tree directory!\n" f"{work_tree} doesn't exist"
                raise WorktreeMissing(msg)

    # Query Git
    @cached_property
    def short_status(self) -> List[str]:
        """List of lines in git status porecelain=v1 format (except renames)."""
        output = subprocess.run(
            self._git_base
            + ["status", "--short", "--untracked-files=no", "--porcelain", "-z"],
            text=True,
            capture_output=True,
        ).stdout

        pieces = [p for p in output.split("\x00") if p]
        length = len(pieces)
        pos = 0
        result = []
        while pos < length:
            if pieces[pos][0] == "R":
                stem = pieces[pos][:3]
                old = pieces[pos + 1]
                new = pieces[pos][3:]
                sep = " -> "
                result.append(f"{stem}{old}{sep}{new}")
                pos += 2
            else:
                result.append(pieces[pos])
                pos += 1
        return result

    @property
    def tracked(self) -> List[str]:
        output_lines = subprocess.run(
            self._git_base
            + ["ls-tree", "--full-tree", "--full-name", "-r", "HEAD", "-z"],
            text=True,
            capture_output=True,
        ).stdout.split("\x00")
        return [row.split("\t")[-1] for row in output_lines if len(row) > 0]

    @cached_property
    def list_all(self) -> List[str]:
        """List of all files in repo [+new adds, -things going ]. (relative paths)"""
        include = self.tracked + self.adds_staged + self.renames
        removed = self.deleted_staged + self.oldnames
        all = [f for f in include if f not in removed]
        return sorted(list(set(all)))

    @cached_property
    def _git_str(self) -> str:
        """String representation of _git_base command."""
        return " ".join(self._git_base).strip()

    # ADDS
    @property
    def adds_staged(self) -> List[str]:
        """Returns list of newly added files to the staging area."""
        return [f[3:] for f in self.short_status if f[0] == "A"]

    # DELETES
    @property
    def deleted_staged(self) -> List[str]:
        """Returns all files staged for deletion."""
        return [stat[3:] for stat in self.short_status if stat[0] == "D"]

    @property
    def oldnames(self) -> List[str]:
        """Returns previous name of files renamed in staging area."""
        return [
            stat[3:].split(" -> ")[0] for stat in self.short_status if stat[0] == "R"
        ]

    @property
    def renames(self) -> List[str]:
        return [line.split(" -> ")[1] for line in self.short_status if line[0] == "R"]

    # MODIFIED
    @property
    def modified_staged(self) -> List[str]:
        """Returns files with staged modifications."""
        return [stat[3:] for stat in self.short_status if stat[0] == "M"]

    @property
    def modified_unstaged(self) -> List[str]:
        """Returns all files with unstaged modifications or Deletions."""
        mod_codes = [" M", " D", "MM", "AM"]
        mods = [line[3:] for line in self.short_status if line[:2] in mod_codes]
        renamed_mods = [s.split(" -> ")[1] for s in self.short_status if s[:2] == "RM"]
        return sorted(renamed_mods + mods)

    @cached_property
    def restorables(self) -> List[str]:
        """Returns all files which could be affected by `git restore --staged`."""
        return sorted(self.modified_staged + self.deleted_staged + self.adds_staged)

    # Cache
    def freshen(self) -> None:
        """Deltes @cached_property values which forces recompute on next use.

        Very useful for programs building upon Dotfiles. Allows you to take actions,
        utilize @cached_property values during runtime but request caches be dropped
        so further runs will request new data from `git`
        """
        try:
            del self.short_status
        except AttributeError:
            pass  # ignore failure to delete uncached functions
        try:
            del self.list_all
        except AttributeError:
            pass
        try:
            del self.executables
        except AttributeError:
            pass
        try:
            del self.restorables
        except AttributeError:
            pass

    # All of these functions are breaking from the 'Repository'
    # But I don't yet know how... TODO
    #      __     _
    #     / _|   | |     ___   __ __ __
    #    |  _|   | |    / _ \  \ V  V /
    #   _|_|_   _|_|_   \___/   \_/\_/
    # _|"""""|_|"""""|_|"""""|_|"""""|
    # "`-0-0-'"`-0-0-'"`-0-0-'"`-0-0-'
    # How do these objects interact?
    # Which models of action bring relevance and agency?

    @property
    def list_all_as_path(self) -> List[Path]:
        """List of Path() objects for each file in the repository."""
        return [(Path(self.work_tree) / p) for p in self.list_all]

    @cached_property
    def executables(self) -> List[str]:
        """List of executable dotfiles (relative paths)"""
        return [
            str(Path(e).relative_to(self.work_tree))
            for e in self.list_all_as_path
            if os.access(e, os.X_OK)
        ]

    @cached_property
    def preview_app(self) -> str:
        """Return: bat > batcat > highlight > cat."""
        if shutil.which("bat"):
            return "bat --color=always"
        elif shutil.which("batcat"):
            return "batcat --color=always"
        elif shutil.which("highlight"):
            return "highlight -O ansi"
        else:
            return "cat"


# vim: foldlevel=1 :
