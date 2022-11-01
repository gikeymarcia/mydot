# Mikey Garcia, @gikeymarcia
# https://github.com/gikeymarcia/mydot

from __future__ import annotations
import os
import shutil
import subprocess
from pathlib import Path
from typing import List, Protocol, Optional
from mydot.logging import logging


class Editor(Protocol):
    # TODO: throw error when DOTFILES is not defined
    program: str

    def open(self, files: List[Path], search: Optional[str] = None) -> None:
        """
        Open selected files in a text editorself.
        Optionally, define a search string once files are opened.
        """
        raise NotImplementedError


class UserDefinedEditor(Editor):
    """
    Editor class which takes a binary name and tries to use it as the command
    to open a file with. Does not support search paramters and assumes structure:
        `command-name file1 file2 file3 ...`
    """

    def __init__(self, binary_name: str):
        self.program = binary_name

    def open(self, files: List[Path], search: Optional[str] = None):
        logging.debug(f"UserDefinedEditor:")
        if search:
            pass
        if shutil.which(self.program):
            print(f"Reading EDITOR={self.program} from environment")
            subprocess.run([self.program] + files)
        else:
            print(f"Could not find program: {self.program}")
            print("Selections made:\n")
            for f in files:
                print(f"\t{f}")


class MissingEditor(Editor):
    program = "missing"

    def open(self, files: List[Path], search: Optional[str] = None):
        logging.debug("entered MissingEditor.open()")
        if search is None:
            pass
        else:
            logging.debug(f"Missing editor search term: {search}")
            for file in files:
                subprocess.run(
                    [
                        "grep",
                        "--context=5",
                        "--color=auto",
                        "--with-filename",
                        "--line-number",
                        search,
                        file,
                    ]
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
            subprocess.run(base_cmd + files)
        elif count > 1:
            subprocess.run(base_cmd + ["-O"] + files)


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
            subprocess.run(base_cmd + ["-O"] + files)


def find_editor() -> Editor:
    """
    Find a suitable text editor and return as an Editor object.
    """
    logging.debug("find_editor() begins")
    opts = {
        "nvim": Neovim(),
        "vim": Vim(),
        "nano": Nano(),
    }
    env = os.getenv("EDITOR", None)
    logging.debug(f"env EDITOR={env}")
    if env:
        if env in opts:
            return opts[env]
        else:
            return UserDefinedEditor(env)
    editors_to_try = ["nvim", "vim", "nano", "kate", "gedit"]
    logging.debug(f"Searching for viable editors: {editors_to_try}")
    for ed in editors_to_try:
        if shutil.which(ed):
            logging.debug(f"Found editor in $PATH: {ed}")
            if ed in opts:
                return opts[ed]
            else:
                return UserDefinedEditor(ed)
    else:
        logging.debug(f"Failed to find any of: {editors_to_try}")
        return MissingEditor()


# vim: foldlevel=0:
