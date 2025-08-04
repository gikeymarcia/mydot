import os
import subprocess
import sys
from typing import List, Optional, Protocol
from pathlib import Path

import pydymenu

from mydot.clip import Clipper, find_clipper
from mydot.editor import Editor, find_editor
from mydot.logging import logging
from mydot.repository import Repository


class Actions(Protocol):
    def run(self):
        raise NotImplementedError


class EditFiles(Actions):
    def __init__(self, src_repo: Repository, editor: Optional[Editor] = None) -> None:
        self.repo: Repository = src_repo
        self.editor: Editor = find_editor() if editor is None else editor
        logging.debug(f"Editing a file __init__ object complete.")

    def run(self) -> List[Path]:
        edit_queue = pydymenu.fzf(
            self.repo.list_all,
            prompt="Pick file(s) to edit: ",
            multi=True,
            preview=f"{self.repo.preview_app}" + " {}",
        )
        logging.debug(f"return of edit file selector: {edit_queue}")
        if edit_queue is None:
            sys.exit("No selection made. Cancelling action.")
        else:
            absolute_paths = [Path(sel).absolute() for sel in edit_queue]
            logging.debug(f"absolute paths passed to {self.editor}:\n{absolute_paths}")
            self.editor.open(absolute_paths)
            self.repo.freshen()
            return absolute_paths


class Clipboard(Actions):
    """Interactively select file paths to copy to the clipboard."""

    def __init__(self, repo: Repository, clipper: Optional[Clipper] = None):
        self.repo = repo
        self.clipper = find_clipper() if clipper is None else clipper

    def run(self) -> List[str]:
        # TODO: repo.preview_app is a weird hack, change later
        clips = pydymenu.fzf(
            self.repo.list_all,
            prompt="Pick files to add to the clipboard: ",
            multi=True,
            preview=f"{self.repo.preview_app}" + " {}",
        )
        if clips is None:
            sys.exit("No selection made. Cancelling action.")
        else:
            absolute_paths = [str((self.repo.work_tree / c).resolve()) for c in clips]
            combined = " ".join(absolute_paths)
            self.clipper.clip(combined)
            return absolute_paths


class GitPassthrough(Actions):
    """Run git commands on the given repository."""

    def __init__(self, repo: Repository, git_cmd: List[str]):
        self.repo = repo
        self.cmd = git_cmd

    def run(self):
        os.chdir(self.repo.run_from)
        subprocess.run(self.repo._git_base + self.cmd)


class AddChanges(Actions):
    def __init__(self, src_repo: Repository):
        self.repo = src_repo

    def run(self) -> List[str]:
        modified_unstaged = self.repo.modified_unstaged
        if modified_unstaged:
            adding = pydymenu.fzf(
                modified_unstaged,
                prompt="Choose changes to add: ",
                multi=True,
                preview=f"{self.repo._git_str} diff --color --minimal -- " + "{}",
            )
            if adding is None:
                sys.exit("No selection made. No changes will be staged.")
            else:
                subprocess.run(self.repo._git_base + ["add", "-v", "--"] + adding)
                self.repo.freshen()
                return adding
        else:
            sys.exit("No unstaged changes to 'add'.")


class ExportTar(Actions):
    def __init__(self, src_repo: Repository):
        self.repo = src_repo

    def run(self):
        # TODO: incorporate a 'privatemask' feature
        os.chdir(self.repo.work_tree)
        tarball = self.repo.work_tree / "dotfiles.tar.gz"
        tar_cmd = (
            ["tar", "cvzf", tarball]
            + self.repo.list_all
            + [self.repo.bare_repo.relative_to(self.repo.work_tree)]
        )
        subprocess.run(tar_cmd)
        print(
            "-" * 20,
            "tarball ready. Place in work-tree and expand with:",
            "tar xvf dotfiles.tar.gz",
            sep="\n",
        )
        return tarball


class RunExecutable(Actions):
    def __init__(self, src_repo: Repository):
        self.repo = src_repo

    def run(self) -> str:
        """Interactively choose an executable to run. Optionally add arguements."""
        exe = pydymenu.fzf(
            self.repo.executables,
            prompt="Pick a file to run: ",
            multi=False,
            preview=f"{self.repo.preview_app}" + " {}",
        )
        if exe is None:
            sys.exit("No selection made. Cancelling action.")
        else:
            self.selection = exe[0]
            logging.debug(f"Executable file choosen: {self.selection}")
            os.chdir(self.repo.work_tree)
            command = self.script_plus_args(self.selection)
            subprocess.run(command)
            return str(exe[0])

    def script_plus_args(self, selection: str) -> List[str]:
        """Optionally add arguements to a selected script."""
        print("\nAdd script arguments, press ENTER to run\n")
        script_args = input(f"{selection} ").strip()
        if len(script_args) > 0:
            return [str(selection)] + script_args.split()
        else:
            return [str(selection)]


class Grep(Actions):
    def __init__(self, src_repo: Repository, regexp: list[str]):
        self.repo = src_repo
        self.regexp = regexp
        self.joined = self.join_args(regexp)
        logging.debug(f"Making Grep Object: {repr(self)}")

    def __repr__(self):
        return f"\nrepo: {self.repo.bare_repo}\nregexp: {self.regexp}\njoined: {self.joined}"

    def join_args(self, regexp: list[str]) -> str:
        out = ""
        for item in regexp:
            if '|' in item:
                out = out + f" '{item}'"
            else:
                out = out + f' {item}'
        return out

    def run(self):
        """Interactively choose dotfiles to open in text editor."""
        # LATER make it work for multiple regex searches
        proc = subprocess.run(
            ["grep", "-I", "-l"] + self.regexp + self.repo.list_all,
            capture_output=True,
            text=True,
        )
        hits = [h for h in proc.stdout.split("\n") if len(h) > 0]
        if len(hits) == 0:
            sys.exit("No matches for your regex search found in tracked dotfiles.")
        choices = pydymenu.fzf(
            hits,
            prompt="Choose files to open: ",
            multi=True,
            preview=f"grep {self.joined} -n --context=3 --color=always" + " {}",
        )
        if choices is not None:
            editor = find_editor()
            logging.debug(f"Grep.run() search term: {self.regexp}")
            editor.open([Path(file).absolute() for file in choices], search=self.regexp)
            self.repo.freshen()
            return choices
        else:
            sys.exit("No selections made. Cancelling action.")


class Restore(Actions):
    def __init__(self, src_repo: Repository) -> None:
        self.repo = src_repo
        self.result: Optional[List[str]] = None

    def run(self) -> None:
        # Guard clause when nothing to restore
        if self.repo.restorables is None:
            self.repo.show_status()
            sys.exit("\nNo staged changes to restore.")

        restores = pydymenu.fzf(
            self.repo.restorables,
            prompt="Choose changes to REMOVE from the staging area: ",
            multi=True,
            preview=f"{self.repo._git_str} diff --color --minimal --staged -- " + "{}",
        )
        if restores:
            subprocess.run(
                self.repo._git_base + ["restore", "--staged", "--"] + restores
            )
            self.repo.freshen()
            self.result = restores
        else:
            sys.exit("No selection made. No files will be unstaged.")


class DiscardChanges(Actions):
    def __init__(self, src_repo: Repository) -> None:
        self.repo = src_repo
        self.result: Optional[List[str]] = None

    def run(self):
        """Discard changes from file(s) in the working directory."""
        unstaged = self.repo.modified_unstaged

        # Guard clause for when there are no unstaged changes.
        if unstaged is None:
            self.repo.show_status()
            sys.exit("\nNo unstaged changes to discard.")

        discards = pydymenu.fzf(
            unstaged,
            prompt="Choose changes to discard: ",
            multi=True,
            preview=f"{self.repo._git_str} diff --color --minimal HEAD -- " + "{}",
        )
        # Guard clause when no selection is made
        if discards is None:
            sys.exit("No selection made. No changes will be discarded.")

        subprocess.run(self.repo._git_base + ["restore", "--"] + discards)
        self.repo.freshen()
        self.result = discards


# vim: foldlevel=1 :
