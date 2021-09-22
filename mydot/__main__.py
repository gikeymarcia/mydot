#!/usr/bin/env python3
# Mikey Garcia, @gikeymarcia
# https://github.com/gikeymarcia/mydot

import argparse

from mydot import Dotfiles
from mydot.console import my_theme, rich_text


rich_str = {
    "prog": rich_text("[code]python -m mydot[/]", theme=my_theme),
    "desc": rich_text(
        "[cool]Manage[/] and [edit]edit[/] [code]$HOME[/] dotfiles "
        "using [strong]Python + git[/] = [bold red]<3[/]",
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
    "--tar",
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
    "-ls",
    "--list",
    help="list all files in the repo",
    action="store_true",
)
args, extras = parser.parse_known_args()
dotfiles = Dotfiles()

if args.edit:
    dotfiles.edit_files()
elif args.add:
    dotfiles.add_changes()
elif args.status:
    dotfiles.show_status()
elif args.list:
    [print(file) for file in dotfiles.list_all]
elif args.grep:
    dotfiles.grep(args.grep)
elif args.run_executable:
    dotfiles.run_executable()
elif args.restore:
    dotfiles.restore()
elif args.tar:
    dotfiles.make_tar()
elif len(extras) > 1 and extras[0] == "git":
    dotfiles.git_passthrough(extras)
else:
    parser.parse_args(["-h"])

# TODO: Usability at the CLI
# d. --discard throw away work tree changes and restore a file to state @ HEAD
# d. --private build up a filter of files marked 'private'
#   - hide from previews
#   - default hide from --tar
#   - consider relation to other features
# d. --clipboard copy choosen file locations to clipboard
# d. --branch switch to or checkout branches
# d. --init Initiate bare repo and ask which file to append the aliases to?
#              [.bashrc, .bash_aliases, .bash_profile, .profile, .zshrc]
# d. --import REPO : git clone repo and pull it into your work-tree.
#       If a file would conflict backup for the user in a specified location.
#       future idea: offer fzf selectors to decide what to backup and the rest
#       will be discarded

# vim: foldlevel=0:
