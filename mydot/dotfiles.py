#!/usr/bin/env python3
# Mikey Garcia, @gikeymarcia
# https://github.com/gikeymarcia/mydot

# Standard Library
# https://docs.python.org/3/library/functools.html?highlight=functools#functools.cached_property
from functools import cached_property
from os import X_OK, access, chdir, getenv
from pathlib import Path
from shutil import which
from subprocess import run
from sys import exit as sys_exit
from typing import List, Union

from pydymenu import fzf

from mydot.console import console
from mydot.exceptions import MissingRepositoryLocation, WorktreeMissing
from mydot.system_funcs import script_plus_args
from mydot.clip import Clipper, find_clipper


class Dotfiles:
    """Power up control of your dotfiles with fzf and python."""

    def __init__(
        self,
        local_bare_repo: Union[Path, str, None] = None,
        work_tree: Union[Path, str, None] = None,
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
        chdir(self.work_tree)

    @staticmethod
    def _resolve_repo_location(path_loc: Union[str, Path, None]) -> Path:
        """Decides which dotfile repository location will be used.

        When None is given, try to read $DOTFILES from environment.
        When a location is specified return it's Path
        """
        if path_loc is None:
            if env_val := getenv("DOTFILES", default=None):
                return Path(env_val)
            else:
                raise MissingRepositoryLocation(
                    "No repository specified and no value for $DOTFILES in environment."
                )
        else:
            return Path(path_loc) if isinstance(path_loc, str) else path_loc

    @staticmethod
    def _resolve_work_tree_location(dir: Union[Path, str, None]) -> Path:
        """Define work tree location.

        When None given presume Path.home()
        """
        if dir is None:
            return Path.home()
        else:
            work_tree = Path(dir) if isinstance(dir, str) else dir
            if work_tree.is_dir():
                return work_tree
            else:
                msg = "Missing work-tree directory!\n" f"{work_tree} doesn't exist"
                raise WorktreeMissing(msg)

    def show_status(self) -> None:
        """Short pretty formatted info about the repo state."""
        console.print("Branches:", style="header")
        run(self._git_base + ["branch", "-a"])
        console.print("\nModified Files:", style="header")
        run(self._git_base + ["status", "-s"])

    # ACTIONS
    def edit_files(self) -> List[str]:
        """Interactively choose dotfiles to open in text editor."""
        edits = fzf(
            self.list_all,
            prompt="Pick file(s) to edit: ",
            multi=True,
            preview=f"{self.preview_app}" + " {}",
        )
        if edits is None:
            sys_exit("No selection made. Cancelling action.")
        else:
            if len(edits) == 1:
                run([self.editor, edits[0]])
            else:
                run([self.editor, "-o"] + edits)
            self.freshen()
            return edits

    def grep(self, regex: str) -> List[str]:
        """Interactively choose dotfiles to open in text editor."""
        # LATER make it work for multiple regex searches
        proc = run(
            ["grep", "-I", "-l", regex] + self.list_all,
            capture_output=True,
            text=True,
        )
        hits = [h for h in proc.stdout.split("\n") if len(h) > 0]
        if len(hits) == 0:
            sys_exit("No matches for your regex search found in tracked dotfiles.")
        choices = fzf(
            hits,
            prompt="Choose files to open: ",
            multi=True,
            preview=f"grep {regex} -n --context=3 --color=always" + " {}",
        )
        # TODO: abstract these functions into an Opener(ABC/Protocol)
        if choices is not None:
            if len(choices) == 1:
                run([self.editor, "-c", f"/{regex}", choices[0]])
            else:
                run([self.editor, "-o", "-c", f"/{regex}"] + choices)
            self.freshen()
            return choices
        else:
            sys_exit("No selections made. Cancelling action.")

    def run_executable(self) -> str:
        """Interactively choose an executable to run. Optionally add arguements."""
        exe = fzf(
            self.executables,
            prompt="Pick a file to run: ",
            multi=False,
            preview=f"{self.preview_app}" + " {}",
        )
        if exe is None:
            sys_exit("No selection made. Cancelling action.")
        else:
            command = script_plus_args(Path(self.work_tree) / exe[0])
            run(command)
            return str(exe[0])

    def add_changes(self) -> List[str]:
        """Interactively choose modified files to add to the staging area."""
        if self.modified_unstaged:
            adding = fzf(
                self.modified_unstaged,
                prompt="Choose changes to add: ",
                multi=True,
                preview=f"{self._git_str} diff --color --minimal -- " + "{}",
            )
            if adding is None:
                sys_exit("No selection made. No changes will be staged.")
            else:
                run(self._git_base + ["add", "-v", "--"] + adding)
                self.freshen()
                return adding
        else:
            sys_exit("No unstaged changes to 'add'.")

    def restore(self) -> List[str]:
        """Interactively choose files to remove from the staging area."""
        if self.restorables:
            restores = fzf(
                self.restorables,
                prompt="Choose changes to remove from staging area: ",
                multi=True,
                preview=f"{self._git_str} diff --color --minimal --staged -- " + "{}",
            )
            if restores is None:
                sys_exit("No selection made. No files will be unstaged.")
            else:
                run(self._git_base + ["restore", "--staged", "--"] + restores)
                self.freshen()
                return restores
        else:
            self.show_status()
            sys_exit("\nNo staged changes to restore.")

    def discard_changes(self) -> List[str]:
        """Discard changes from file(s) in the working directory."""
        unstaged = self.modified_unstaged
        if unstaged:
            discards = fzf(
                unstaged,
                prompt="Choose changes to discard: ",
                multi=True,
                preview=f"{self._git_str} diff --color --minimal HEAD -- " + "{}",
            )
            if discards is None:
                sys_exit("No selection made. No changes will be discarded.")
            else:
                run(self._git_base + ["restore", "--"] + discards)
                self.freshen()
                return discards
        else:
            self.show_status()
            sys_exit("\nNo unstaged changes to discard.")

    def make_tar(self) -> Path:
        """Make tarball of dotfiles @ self.work_tree / 'dotfiles.tar.gz'."""
        # TODO: incorporate a 'privatemask' feature
        tarball = self.work_tree / "dotfiles.tar.gz"
        tar_cmd = ["tar", "cvzf", tarball] + self.list_all
        run(tar_cmd)
        print("-" * 20)
        print(
            "tarball ready. Place in work-tree and expand with:\n"
            "tar xvf dotfiles.tar.gz"
        )
        return tarball

    def clip(self, clipper: Clipper = None) -> List[str]:
        """Choose file(s) and copy their path(s) to the clipboard."""
        if clipper is None:
            clipper = find_clipper()
        clips = fzf(
            self.list_all,
            prompt="Pick files to add to the clipboard.",
            multi=True,
            preview=f"{self.preview_app}" + " {}",
        )
        if clips is None:
            sys_exit("No selection made. Cancelling action.")
        else:
            abs_paths = [str((self.work_tree / c).resolve()) for c in clips]
            combined = " ".join(abs_paths)
            clipper.clip(combined)
            return abs_paths

    # PROPERTIES
    @cached_property
    def short_status(self) -> List[str]:
        """List of lines in git status porecelain=v1 format (except renames)."""
        output = run(
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
        output_lines = run(
            self._git_base
            + ["ls-tree", "--full-tree", "--full-name", "-r", "HEAD", "-z"],
            text=True,
            capture_output=True,
        ).stdout.split("\x00")
        return [row.split("\t")[-1] for row in output_lines if len(row) > 0]

    @property
    def adds_staged(self) -> List[str]:
        """Returns list of newly added files to the staging area."""
        return [f[3:] for f in self.short_status if f[0] == "A"]

    @property
    def oldnames(self) -> List[str]:
        """Returns previous name of files renamed in staging area."""
        return [
            stat[3:].split(" -> ")[0] for stat in self.short_status if stat[0] == "R"
        ]

    @property
    def renames(self) -> List[str]:
        return [line.split(" -> ")[1] for line in self.short_status if line[0] == "R"]

    @cached_property
    def list_all(self) -> List[str]:
        """List of all files in repo [+new adds, -things going ]. (relative paths)"""
        include = self.tracked + self.adds_staged + self.renames
        removed = self.deleted_staged + self.oldnames
        all = [f for f in include if f not in removed]
        return sorted(list(set(all)))

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
            if access(e, X_OK)
        ]

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

    @property
    def deleted_staged(self) -> List[str]:
        """Returns all files staged for deletion."""
        return [stat[3:] for stat in self.short_status if stat[0] == "D"]

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

    @cached_property
    def _git_str(self) -> str:
        """String representation of _git_base command."""
        return " ".join(self._git_base).strip()

    @cached_property
    def preview_app(self) -> str:
        """Return: bat > batcat > highlight > cat."""
        if which("bat"):
            return "bat --color=always"
        elif which("batcat"):
            return "batcat --color=always"
        elif which("highlight"):
            return "highlight -O ansi"
        else:
            return "cat"

    @cached_property
    def editor(self) -> str:
        """Preference: $EDITOR > nvim > vim > nano > emacs."""
        if env := getenv("EDITOR", None):
            return env
        else:
            for prog in ["nvim", "vim", "nano", "emacs"]:
                if bin := which(prog):
                    return bin
            else:
                sys_exit("Cannot find a suitable editor, and boy did we look!")

    def git_passthrough(self, args: List[str]):
        """Send commands to git with --git-dir and --work-tree set."""
        chdir(self.run_from)
        run(self._git_base + args[1:])


# vim: foldlevel=1 :
