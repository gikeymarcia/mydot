from rich.console import Console
from rich.theme import Theme

my_theme = Theme(
    {
        "code": "bold green italic",
        "strong": "bold green italic",
        "edit": "blue italic underline bold",
        "cool": "bold blue",
        "link": "yellow underline",
    }
)
console = Console(theme=my_theme)
__all__ = ["my_theme", "console"]
