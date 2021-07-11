from rich.console import Console
from rich.theme import Theme
from typing import Union

my_theme = Theme(
    {
        "code": "bold green italic",
        "strong": "bold green italic",
        "header": "underline bold green",
        "edit": "blue italic underline bold",
        "cool": "bold blue",
        "link": "yellow underline",
    }
)


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


console = Console(theme=my_theme)
__all__ = ["my_theme", "console", "rich_text"]
# vim: foldlevel=4:
