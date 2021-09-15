# Mikey Garcia, @gikeymarcia
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
    "--restore",
    help="Use fzf to interactively choose file(s) to remove from the staging area.",
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
args = parser.parse_args()
dotfiles = Dotfiles()

if args.edit:
    dotfiles.edit_files()
elif args.add:
    dotfiles.add_changes()
elif args.status:
    dotfiles.show_status()
elif args.list:
    for dotfile in dotfiles.list_all:
        print(dotfile)
elif args.restore:
    dotfiles.restore()
else:
    parser.parse_args(["-h"])

# TODO: Usability at the CLI
# Move from --flags to subcommands
# https://docs.python.org/3/library/argparse.html#sub-commands
# d. (stat) default
# d. (add) fzf modified or add -v for List[files]
# d. (branch) switch to or checkout branches
# d. (tar) make tarball (optionally take path for file)
# d. (create) Initiate bare repo and ask which file to append the aliases to?
#              [.bashrc, .bash_aliases, .bash_profile, .profile, .zshrc]

# vim: foldlevel=4:
