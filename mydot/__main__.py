#!/usr/bin/env python3
# Mikey Garcia, @gikeymarcia
# https://github.com/gikeymarcia/mydot

import argparse
import sys
from mydot.logging import logging

from mydot import Repository
from mydot.actions import (
    AddChanges,
    Clipboard,
    DiscardChanges,
    ExportTar,
    GitPassthrough,
    Grep,
    Restore,
    RunExecutable,
    EditFiles,
)
from mydot.console import my_theme, rich_text


def main():
    rich_str = {
        "prog": rich_text("[code]python -m mydot[/]", theme=my_theme),
        "desc": rich_text(
            "[cool]Manage[/] and [edit]edit[/] [code]$HOME[/] dotfiles "
            "using [strong]Python + git + fzf[/] = [bold red]<3[/]",
            theme=my_theme,
        ),
        "epilog": rich_text(
            "For more about dotfiles see: [link]https://www.atlassian.com/git/tutorials/dotfiles[/]",
            theme=my_theme,
        ),
    }

    # https://docs.python.org/3/library/argparse.html#module-argparse
    parser = argparse.ArgumentParser(
        prog=rich_str["prog"],
        description=rich_str["desc"],
        epilog=rich_str["epilog"],
    )
    subparsers = parser.add_subparsers(dest="command")

    subparsers.add_parser("edit", help="Interactively choose file(s) to edit")
    subparsers.add_parser("add", help="Interactively stage changes")
    subparsers.add_parser("status", help="Show repo status")
    subparsers.add_parser("ls", help="List all tracked dotfiles")

    grep_parser = subparsers.add_parser("grep", help="Search repo with regex")
    grep_parser.add_argument("pattern", type=str)

    subparsers.add_parser("run", help="Run a tracked executable")
    subparsers.add_parser("discard", help="Revert unstaged file(s)")
    subparsers.add_parser("restore", help="Unstage file(s)")
    subparsers.add_parser("export", help="Tarball of all tracked files")
    subparsers.add_parser("clip", help="Copy absolute paths to clipboard")

    git_parser = subparsers.add_parser("git", help="Pass commands to git")
    git_parser.add_argument("args", nargs=argparse.REMAINDER)

    args, unknown_args = parser.parse_known_args()
    dotfiles = Repository()
    logging.debug(f"{sys.argv=}")

    match args.command:
        case "edit":
            EditFiles(dotfiles).run()
        case "add":
            AddChanges(dotfiles).run()
        case "status":
            dotfiles.show_status()
        case "ls":
            for file in dotfiles.list_all:
                print(file)
        case "grep":
            Grep(dotfiles, sys.argv[2:]).run()
        case "run":
            RunExecutable(dotfiles).run()
        case "discard":
            DiscardChanges(dotfiles).run()
        case "restore":
            Restore(dotfiles).run()
        case "export":
            ExportTar(dotfiles).run()
        case "clip":
            Clipboard(dotfiles).run()
        case "git":
            logging.info(f'git command: {sys.argv[2:]}')
            GitPassthrough(dotfiles, sys.argv[2:]).run()
        case _:
            parser.print_help()

if __name__ == "__main__":
    main()

# vim: foldlevel=0:
