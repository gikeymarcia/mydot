from pathlib import Path

from mydot.config import (
    DEFAULT_TITLE_FORMAT_NERD,
    DEFAULT_TITLE_FORMAT_PLAIN,
    WatchConfig,
    load_watch_config,
)


GLYPH = ""


def test_defaults_when_no_file(tmp_path: Path):
    cfg = load_watch_config(tmp_path / "missing.ini")
    assert isinstance(cfg, WatchConfig)
    assert cfg.title_format == DEFAULT_TITLE_FORMAT_NERD


def test_reads_title_format(tmp_path: Path):
    p = tmp_path / "config.ini"
    p.write_text("[watch]\ntitle_format = {branch} :: {remote}\n")
    cfg = load_watch_config(p)
    assert cfg.title_format == "{branch} :: {remote}"


def test_reads_theme(tmp_path: Path):
    p = tmp_path / "config.ini"
    p.write_text("[watch]\ntheme = dracula\n")
    cfg = load_watch_config(p)
    assert cfg.theme == "dracula"


def test_default_theme_is_catppuccin_mocha(tmp_path: Path):
    cfg = load_watch_config(tmp_path / "missing.ini")
    assert cfg.theme == "catppuccin-mocha"


def test_missing_section_uses_defaults(tmp_path: Path):
    p = tmp_path / "config.ini"
    p.write_text("[other]\nx = 1\n")
    cfg = load_watch_config(p)
    assert cfg.title_format == DEFAULT_TITLE_FORMAT_NERD


def test_render_title_with_remote():
    cfg = WatchConfig()
    title = cfg.render_title(branch="main", remote="git@host:repo")
    assert "main" in title
    assert "(git@host:repo)" in title


def test_render_title_no_remote_omits_remote():
    cfg = WatchConfig()
    title = cfg.render_title(branch="main", remote="")
    assert "main" in title
    assert "(" not in title  # no remote parens at all
    assert "no remote" not in title


def test_render_title_custom_format_with_remote_suffix():
    cfg = WatchConfig(title_format="[{branch}]{remote_suffix}")
    assert cfg.render_title(branch="main", remote="origin") == "[main] (origin)"
    assert cfg.render_title(branch="main", remote="") == "[main]"


def test_nerd_fonts_default_true(tmp_path):
    cfg = load_watch_config(tmp_path / "missing.ini")
    assert cfg.nerd_fonts is True
    assert GLYPH in cfg.title_format


def test_nerd_fonts_false_drops_glyph_from_default(tmp_path):
    p = tmp_path / "config.ini"
    p.write_text("[watch]\nnerd_fonts = false\n")
    cfg = load_watch_config(p)
    assert cfg.nerd_fonts is False
    assert cfg.title_format == DEFAULT_TITLE_FORMAT_PLAIN
    assert GLYPH not in cfg.title_format


def test_explicit_title_format_wins_over_nerd_fonts(tmp_path):
    """User-supplied title_format is theirs; nerd_fonts only swaps the default."""
    p = tmp_path / "config.ini"
    p.write_text(
        "[watch]\n"
        "nerd_fonts = false\n"
        f"title_format = XY\n"
    )
    cfg = load_watch_config(p)
    assert cfg.title_format == f"XY"
