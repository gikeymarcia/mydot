import os
import subprocess
import sys
from typing import List, Optional, Protocol

import pydymenu

from mydot.clip import Clipper, find_clipper
from mydot.repository import Repository


class Actions(Protocol):
    def run(self):
        raise NotImplementedError


class Clipboard(Actions):
    """Interactively select file paths to copy to the clipboard."""

    def __init__(self, repo: Repository, clipper: Optional[Clipper] = None):
        self.repo = repo
        self.clipper = find_clipper() if clipper is None else clipper

    def run(self):
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
