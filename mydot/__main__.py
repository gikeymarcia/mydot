# Mikey Garcia, @gikeymarcia
import argparse
from pathlib import Path
from typing import Union

from rich.console import Console
from rich.theme import Theme

from mydot import Dotfiles
from mydot.console import my_theme, console


def rich_text(
    rich_markup: str,
    theme: Union[None, Theme] = None,
    **rich_print_opts,
) -> str:
    """Accept rich markup and return stylized text suitable for print()."""
    temp_console = Console(theme=theme)
    with temp_console.capture() as formatted:
        temp_console.print(rich_markup, **rich_print_opts)
    return formatted.get().strip()


console.print("[strong]rich console print[/]", justify="center")

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
args = parser.parse_args(["-ls"])

if args.edit:
    console.log("EDIT", log_locals=True)
elif args.status:
    console.log("STATUS", log_locals=True)
elif args.list:
    console.log("LIST", log_locals=True)
else:
    parser.parse_args(["-h"])

# vim: foldlevel=4:
