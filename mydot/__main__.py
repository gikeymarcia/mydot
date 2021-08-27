# Mikey Garcia, @gikeymarcia
import argparse

from mydot import Dotfiles
from mydot.console import console, my_theme, rich_text


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
    help="Use fzf to interactively choose files to edit",
    action="store_true",
)
group.add_argument(
    "-s", "--status", help="Show status of dotfiles repo", action="store_true"
)
group.add_argument(
    "-a",
    "--add",
    help="Interactively add changes your dotfiles",
    action="store_true",
)
group.add_argument(
    "-ls",
    "--list",
    help="Show list of all files in the repo",
    action="store_true",
)
args = parser.parse_args()
dfs = Dotfiles()

if args.edit:
    dfs.edit_files()
elif args.add:
    adds = dfs.add()
    # console.print(f"selected dotfiles = {adds}")
elif args.status:
    dfs.show_status()
elif args.list:
    for dotfile in dfs.list_all:
        print(dotfile)
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
