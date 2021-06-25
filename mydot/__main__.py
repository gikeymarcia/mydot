from mydot import Dotfiles
import argparse
from pathlib import Path


# https://docs.python.org/3/library/argparse.html#module-argparse
parser = argparse.ArgumentParser(
    prog="mydot command-line interface",
    description="Manage and edit $HOME dotfiles using Python + git = <3",
    epilog="For more about dotfiles see: https://www.atlassian.com/git/tutorials/dotfiles",
)
group = parser.add_mutually_exclusive_group()
group.add_argument(
    "-e",
    "--edit",
    help="Use fzf to interactively choose files to edit",
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
    help="Show list of all files in the repo",
    action="store_true",
)
args = parser.parse_args()
print(f"{args = }")

if args.edit:
    print("EDIT")
elif args.status:
    print("STATUS")
elif args.list:
    print("LIST")
else:
    parser.parse_args(["-h"])
