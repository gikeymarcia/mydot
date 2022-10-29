# Mikey Garcia, @gikeymarcia
# https://github.com/gikeymarcia/mydot

from __future__ import annotations
import os
import shutil
import subprocess
from pathlib import Path
from typing import List, Protocol, Optional


class Editor(Protocol):
    # TODO: throw error when DOTFILES is not defined
    program: str

    def open(self, files: List[Path], search: Optional[str] = None) -> None:
        """
        Open selected files in a text editorself.
        Optionally, define a search string once files are opened.
        """
        raise NotImplementedError


class MissingEditor(Editor):
    program = "missing"

    def open(self, files: List[Path], search: Optional[str] = None):
        if search:
            for file in files:
                subprocess.run(
                    ["grep", "--context=5", "--color=auto", "--line-number", file]
                )
        print("\n\nNo suitable editor found on the system, and boy did we look!\n")
        print("Files selected:\n")
        for file in files:
            print(f"\t{file}")


class Nano(Editor):
    program = "nano"

    def open(self, files: List[Path], search: Optional[str] = None):
        if len(files) > 0:
            if search is None:
                subprocess.run(["nano"] + files)
            else:
                # nano +c/Foo file
                subprocess.run(["nano", f"+c/{search}"] + files)


class Neovim(Editor):
    program = "nvim"

    def open(self, files: List[Path], search: Optional[str] = None):
        count = len(files)
        base_cmd = ["nvim"]
        if search:
            base_cmd = base_cmd + ["-c", f"/{search}"]
        if count == 1:
            subprocess.run(base_cmd + [files[0]])
        elif count > 1:
            subprocess.run(base_cmd + ["-o"] + files)


class Vim(Editor):
    program = "vim"

    def open(self, files: List[Path], search: Optional[str] = None):
        count = len(files)
        base_cmd = ["vim"]
        if search:
            base_cmd = base_cmd + ["-c", f"/{search}"]
        if count == 1:
            subprocess.run(base_cmd + [files[0]])
        elif count > 1:
            subprocess.run(base_cmd + ["-o"] + files)


def find_editor() -> Editor:
    """
    Find a suitable text editor and return as an Editor object.
    """
    opts = {
        "nvim": Neovim(),
        "vim": Vim(),
        "nano": Nano(),
    }
    env = os.getenv("EDITOR", None)
    if env:
        if env in opts:
            return opts[env]
        else:
            return MissingEditor
    if env in opts:
        return opts[env]
    else:
        for ed in ["nvim", "vim", "nano"]:
            if shutil.which(ed):
                return opts[ed]
        else:
            return MissingEditor()


# vim: foldlevel=0:
