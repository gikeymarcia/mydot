#!/usr/bin/env python3
# Mikey Garcia, @gikeymarcia
# https://github.com/gikeymarcia/mydot

import argparse

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
    group = parser.add_mutually_exclusive_group()
    group.add_argument(
        "-e",
        "--edit",
        help="Use fzf to interactively choose file(s) to open in your $EDITOR",
        action="store_true",
    )
    group.add_argument(
        "-a",
        "--add",
        help="Use fzf to interactively stage changes to your dofiles",
        action="store_true",
    )
    group.add_argument(
        "-r",
        "--run",
        help="Interactively choose an excutable file/script to run.",
        action="store_true",
        dest="run_executable",
    )
    group.add_argument(
        "-g",
        "--grep",
        help="regex search over each non-binary file in the repo. Select from hits.",
        type=str,
    )
    group.add_argument(
        "--restore",
        help="Use fzf to interactively choose file(s) to remove from the staging area.",
        action="store_true",
    )
    group.add_argument(
        "--discard",
        help="Revert unstaged file(s) back to their state at the last commit.",
        action="store_true",
    )
    group.add_argument(
        "--clip",
        help="Put absolute file path(s) into the clipboard.",
        action="store_true",
    )
    group.add_argument(
        "--export",
        help="Make a tarball of tracked dotfiles @ work-tree/dotfiles.tar.gz",
        action="store_true",
    )
    group.add_argument(
        "-s",
        "--status",
        help="Show status of dotfiles repo",
        action="store_true",
    )
    group.add_argument(
        "-l",
        "--list",
        help="List all dotfiles in the work tree",
        action="store_true",
    )
    args, extra_args = parser.parse_known_args()
    dotfiles = Repository()
    # TODO add --history
    # $(git log --oneline -- bootstrap.yml | awk '{print $1'} | fzf --preview="git show {}:bootstrap.yml"')
    # flow: d. --history
    #   1. pick file
    #   2. get list of hashes
    #   3. fzf picker with preview of each version
    #   4. Upon selection open file in split view with current version


    if args.edit:
        EditFiles(dotfiles).run()
    elif args.add:
        AddChanges(dotfiles).run()
    elif args.status:
        dotfiles.show_status()
    elif args.list:
        [print(file) for file in dotfiles.list_all]
    elif args.grep:
        Grep(dotfiles, args.grep).run()
    elif args.run_executable:
        RunExecutable(dotfiles).run()
    elif args.discard:
        DiscardChanges(dotfiles).run()
    elif args.restore:
        Restore(dotfiles).run()
    elif args.export:
        ExportTar(dotfiles).run()
    elif args.clip:
        Clipboard(dotfiles).run()
    elif len(extra_args) > 1 and extra_args[0] == "git":
        GitPassthrough(dotfiles, extra_args[1:]).run()
    else:
        parser.parse_args(["-h"])

if __name__ == "__main__":
    main()
# vim: foldlevel=0:
