"""Config loader for mydot. Reads ~/.config/mydot/config.ini."""
from __future__ import annotations

import configparser
from dataclasses import dataclass
from pathlib import Path


# Default title with Nerd Font octicon nf-oct-git_branch (U+F418).
# Renders as a branch glyph in any Nerd Font; a tofu box otherwise.
# Set `nerd_fonts = false` in config.ini to swap to the plain-text default.
DEFAULT_TITLE_FORMAT_NERD  = "mydot --  {branch}{remote_suffix}"
DEFAULT_TITLE_FORMAT_PLAIN = "mydot -- {branch}{remote_suffix}"
DEFAULT_TITLE_FORMAT = DEFAULT_TITLE_FORMAT_NERD  # back-compat alias
DEFAULT_THEME = "catppuccin-mocha"  # name of a built-in Textual theme


def default_config_path() -> Path:
    return Path.home() / ".config" / "mydot" / "config.ini"


@dataclass
class WatchConfig:
    title_format: str = DEFAULT_TITLE_FORMAT_NERD
    theme: str = DEFAULT_THEME
    nerd_fonts: bool = True

    def render_title(self, *, branch: str, remote: str) -> str:
        remote_suffix = f" ({remote})" if remote else ""
        return self.title_format.format(
            branch=branch or "(detached)",
            remote=remote,
            remote_suffix=remote_suffix,
        )


def load_watch_config(path: Path | None = None) -> WatchConfig:
    path = path if path is not None else default_config_path()
    if not path.is_file():
        return WatchConfig()
    parser = configparser.ConfigParser()
    parser.read(path)
    if not parser.has_section("watch"):
        return WatchConfig()
    section = parser["watch"]
    nerd_fonts = section.getboolean("nerd_fonts", True)
    default_title = DEFAULT_TITLE_FORMAT_NERD if nerd_fonts else DEFAULT_TITLE_FORMAT_PLAIN
    return WatchConfig(
        title_format=section.get("title_format", default_title),
        theme=section.get("theme", DEFAULT_THEME),
        nerd_fonts=nerd_fonts,
    )
