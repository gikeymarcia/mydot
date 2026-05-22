# `d. watch` — lazygit-style TUI

A Textual-based two-pane TUI for browsing, staging, and committing
dotfile changes. Designed to live in a side tmux pane next to your editor
and update live as you save files.

## Launch

```bash
d. watch
# or:
python -m mydot watch
```

Quit with `q`.

## Layout

```
┌─────────────────────────────────┬──────────────────────────────────┐
│ file list                       │ diff for highlighted file        │
│    ● mydot/watch.py       │ diff --git a/...                 │
│    ○ tests/test_watch_tui.py    │ @@ -1,5 +1,7 @@                  │
│    ◐ CHANGELOG.md  [partially…] │  ...                             │
│                                 │                                  │
└─────────────────────────────────┴──────────────────────────────────┘
 mydot --  v0.13-dev (git@host:repo)               s u c …
```

- **Left pane** — alphabetically sorted list of files that have any
  uncommitted change. The position is stable: staging/unstaging never
  shuffles the rows.
- **Right pane** — colored `git diff` for the highlighted row.
- **Title bar** — branch (with Nerd Font branch glyph) and remote, if
  any.
- **Footer** — discoverable keybindings.

## File states

The leading status marker tells you the state at a glance:

| Marker | State      | Color       | Notes                                                 |
|--------|------------|-------------|-------------------------------------------------------|
| `○`    | unstaged   | red         | worktree edits, nothing staged                        |
| `●`    | staged     | green       | staged, no further worktree edits                     |
| `◐`    | partial    | red + green `[partially staged]` | staged + more worktree edits (git "MM") |

For partial files the right pane shows the **worktree (unstaged) diff** —
the "what's left to stage" view.

## Keybindings

### Navigation

| Key         | Action                                |
|-------------|---------------------------------------|
| `j` / `↓`   | Cursor down                           |
| `k` / `↑`   | Cursor up                             |
| `gg`        | Jump to top                           |
| `G`         | Jump to bottom                        |
| `tab`       | Toggle focus between list and diff pane |

The `gg` two-key sequence works like vim — the first `g` arms a 500ms
window for the second.

### Staging

| Key      | Action                                              |
|----------|-----------------------------------------------------|
| `s`      | Stage (no-op on already-fully-staged)               |
| `u`      | Unstage (no-op on fully-unstaged)                   |
| `space`  | Toggle: stage if not fully staged, otherwise unstage |

### File operations

| Key             | Action                                            |
|-----------------|---------------------------------------------------|
| `e` / `enter`   | Open in `$EDITOR` (same chain as `d. edit`)       |
| `yy`            | Yank absolute path to clipboard (same chain as `d. clip`) |

The editor opens via `find_editor()` (`$EDITOR` env var → Neovim → Vim →
Nano → fallback). The clipper uses `find_clipper()` (wl-copy → xclip →
xsel → pbcopy → terminal-print fallback).

### Commit

| Key | Action |
|-----|--------|
| `c` | Run `git commit` with full `.gitconfig` editor flow |

`c` suspends the TUI and shells to **plain `git commit`** (no `-F`, no
`-m`), so your full `.gitconfig` setup runs:

- `commit.template` populates the message buffer
- `commit.verbose` appends the diff below the cut line
- `commit.cleanup` honored (strip / whitespace / scissors)
- `prepare-commit-msg` / `commit-msg` hooks fire
- `commit.gpgsign` + TTY passphrase prompts work
- Aliases, custom `core.editor`, etc.

If you abort the editor (empty message) the commit aborts; the TUI
returns and tells you what happened.

### Misc

| Key | Action            |
|-----|-------------------|
| `r` | Refresh now       |
| `?` | Help modal        |
| `q` | Quit              |

`?` opens a modal showing all keybindings — close with `esc`, `q`, or
`?` again.

## Refresh / polling

The TUI polls `git status` once per second so it stays current while you
edit files in another pane. After any in-TUI mutation (stage, unstage,
commit, edit) the refresh runs immediately.

Polling cost is minimal — `git status --porcelain` against a bare repo's
index is sub-50ms for hundreds of tracked files.

## Themes

`d. watch` ships using **Catppuccin Mocha** by default and pulls colors
from whichever Textual built-in theme is active. Press **Ctrl+P** and
type "Change theme" for the live palette switcher. All 20 of Textual's
built-in themes work:

```
ansi-dark           ansi-light          atom-one-dark       atom-one-light
catppuccin-frappe   catppuccin-latte    catppuccin-macchiato catppuccin-mocha
dracula             flexoki             gruvbox             monokai
nord                rose-pine           rose-pine-dawn      rose-pine-moon
solarized-dark      solarized-light     textual-dark        textual-light
tokyo-night
```

Set your preferred default in the config file (next section).

## Configuration

Reads `~/.config/mydot/config.ini` (XDG default). All keys optional.

```ini
[watch]
theme        = catppuccin-mocha
nerd_fonts   = true
title_format = mydot --  {branch}{remote_suffix}
```

### `theme` (default `catppuccin-mocha`)

Name of any Textual built-in theme (see list above). Bad names fall back
silently to the Textual default.

### `nerd_fonts` (default `true`)

Controls whether `d. watch` injects Nerd Font glyphs:

- `true`  — branch glyph in title, `` selector arrow in the list
- `false` — drops the branch glyph from the default title and uses `>`
  as the selector arrow. Use this on terminals without a Nerd Font.

Note: an explicit `title_format` overrides the auto-swap — the flag only
controls which **default** template is picked.

### `title_format` (default depends on `nerd_fonts`)

Format string for the window title. Placeholders:

| Placeholder        | Expansion                                                    |
|--------------------|--------------------------------------------------------------|
| `{branch}`       | Current branch name (or `(detached)` if HEAD is detached)    |
| `{remote}`       | First remote URL (typically `origin`), or empty              |
| `{remote_suffix}`| `" ({remote})"` when a remote exists, otherwise empty       |

Built-in defaults:

```
nerd_fonts = true   → "mydot --  {branch}{remote_suffix}"
nerd_fonts = false  → "mydot -- {branch}{remote_suffix}"
```

Examples:

```ini
title_format = [{branch}]{remote_suffix}      # → "[master] (origin)"
title_format = WATCH {branch}                   # → "WATCH master"
title_format = {branch} @ {remote}            # → "master @ git@host:..."
                                                  #   (always shows remote; empty if none)
```

## Terminal transparency

`d. watch` runs in Textual's `ansi_color=True` mode so cells without an
explicit truecolor background emit no SGR `48;…` code → terminal
transparency shows through (Ghostty, Kitty, WezTerm, etc.).

The highlighted row has **no background tint** because alpha compositing
in Textual fights terminal transparency. The selector glyph (``
or `>`) is the selection cue instead.

## Color choice notes

Unstaged red and staged green are mapped to Textual's theme variables
`$error` and `$success`. Per-theme palettes are chosen by the theme
authors; both are verified to meet WCAG AA contrast against the default
background in the bundled Catppuccin Mocha theme:

- Red `#f38ba8` on base `#1e1e2e` — 7.08:1 (AA)
- Green `#a6e3a4` on base `#1e1e2e` — 11.05:1 (AAA)

If you switch themes and find a state hard to read, file an issue — the
fix lives in the theme, not in `d. watch`.
