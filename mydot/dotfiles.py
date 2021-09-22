#!/usr/bin/env python3
# Mikey Garcia, @gikeymarcia
# https://github.com/gikeymarcia/mydot

# Standard Library
# https://docs.python.org/3/library/functools.html?highlight=functools#functools.cached_property
from functools import cached_property
from os import X_OK, access, chdir, getenv
from pathlib import Path
import re
from shutil import which
from subprocess import run
from sys import exit as sys_exit
from typing import List, Union

from pydymenu import fzf

from mydot.console import console
from mydot.exceptions import MissingRepositoryLocation, WorktreeMissing
from mydot.system_funcs import script_plus_args


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
        self._git_base = [
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
        restorables = sorted(
            list(set(self.modified_staged + self.deleted_staged + self.adds_staged))
        )
        if restorables:
            restores = fzf(
                restorables,
                prompt="Choose changes to remove from staging area: ",
                multi=True,
                preview=f"{self._git_str} diff --color --minimal HEAD -- " + "{}",
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

        def reformat_renames(m):
            """Reformat renamed entry output from 'git status -z'.

            New format: '\x00R[ MD] oldname -> rename\x00'
            Important: this is different than the format stated in 'man git-status'
            """
            return "\x00" + m.group(1) + m.group(3) + " -> " + m.group(2) + "\x00"

        renamed_regex = r"\x00(R[ MD] )(.*)\x00(.*)\x00"
        # https://docs.python.org/3/library/re.html#text-munging
        reformatted = re.sub(renamed_regex, reformat_renames, output).split("\x00")
        return [statusline for statusline in reformatted if len(statusline) > 0]

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
        if len(self.short_status) == 0:
            return []
        else:
            rename_lines = [l for l in self.short_status if l[0] == "R"]
            if len(rename_lines) > 0:
                rename_files = [f.split(" -> ")[1] for f in rename_lines]
                return rename_files
            else:
                return []

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
        return [stat[3:] for stat in self.short_status if stat[1] in ["M", "D"]]

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
        run(self._git_base + args[1:])


# vim: foldlevel=1 :
