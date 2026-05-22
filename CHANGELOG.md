All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).


## [0.13.0] - 2026-05-21

### Added

- `watch` subcommand: a lazygit-style Textual TUI. Left pane lists files
  with uncommitted changes; right pane shows the colored diff for the
  highlighted file. Polls `git` once per second so you can leave it open
  in a tmux pane while editing elsewhere. Full reference in
  [`docs/watch.md`](docs/watch.md).
- Keybindings:
  - **Navigation**: `j`/`k`/`↑`/`↓`, `gg` (top), `G` (bottom), `tab`
    (toggle list ↔ diff pane). `j`/`k`/`gg`/`G` route to whichever pane
    has focus.
  - **Staging**: `s` stage, `u` unstage, `space` toggle.
  - **File ops**: `e` / `Enter` opens in `$EDITOR` (reuses `find_editor()`
    from `d. edit`); `yy` yanks the absolute path to the clipboard
    (reuses `find_clipper()` from `d. clip`).
  - **Commit**: `c` suspends the TUI and shells out to plain `git commit`
    so your full `.gitconfig` editor flow fires (`commit.template`,
    `commit.verbose`, `commit.cleanup`, `prepare-commit-msg` /
    `commit-msg` hooks, GPG signing with TTY passphrase, aliases).
  - **Misc**: `r` refresh, `?` help modal, `q` quit.
- Three file states with distinct markers and colors:
  - `○` unstaged (red)
  - `●` staged (green)
  - `◐` partial — staged + further worktree edits, git "MM" status;
    red with green `[partially staged]` suffix.
- Row order is alphabetically stable: staging/unstaging never shuffles
  the cursor.
- File entries colored by state: unstaged in `$error` (red), staged in
  `$success` (green). Colors come from the active Textual theme — switch
  themes live with `Ctrl+P` → "Change theme". Catppuccin Mocha is the
  default; all 20 of Textual's built-in themes (Dracula, Nord, Gruvbox,
  Tokyo Night, Solarized, Rose Pine, etc.) work out of the box.
- Window title shows the current branch with a Nerd Font branch glyph
  and the remote URL only when one is configured. Set `nerd_fonts = false`
  to drop the glyph from the default (handy on terminals without a Nerd
  Font installed). Title is also customizable via the `title_format` key
  with `{branch}` / `{remote}` / `{remote_suffix}` placeholders (the
  suffix expands to `" ({remote})"` only if a remote exists):

  ```ini
  [watch]
  nerd_fonts   = true
  title_format = mydot --  {branch}{remote_suffix}
  theme        = catppuccin-mocha
  ```

## [0.12.0] - 2026-04-22

### Fixed

- Files staged with `git add` *inside* a submodule (but not yet committed by
  the inner git) now appear in `list_all`. Previously `_list_submodule_files`
  ran `git ls-tree HEAD` inside each submodule, which ignored the submodule's
  index — so a file you'd staged in the submodule was invisible to `d. edit`
  until you committed it. Now it reads `git ls-files --stage`, matching the
  picker's "files you could edit" semantics.

## [0.11.0] - 2026-04-18

### Added

- `cd` subcommand: pick a dotfile via fzf, view its directory contents,
  then drop into a subshell at that location. Supports `$MYDOT_CD_CMD`
  to override the default listing command (`ls -lA --color=auto`).

## [0.10.0] - 2026-04-17

### Added

- Wayland clipboard support: `WlCopy` clipper using `wl-copy`.
- Clipper discovery now prefers `wl-copy` over X11 clippers
  (`wl-copy > xclip > xsel > pbcopy > terminal fallback`).

### Fixed

- Staged-but-uncommitted submodules now appear in `list_all`. Previously,
  `git add`-ing a submodule without committing left it invisible to all
  pickers (edit, ls, fzf, clip, grep, export, history).

## [0.9.2] - 2026-04-14

### Added

- `-v` / `--version` flag on the CLI.

### Fixed

- `scripts/build.sh` uses `python -m build` instead of the deprecated
  `python setup.py sdist bdist_wheel`.
- `scripts/build.sh` uploads via `-r testpypi` / `-r pypi` aliases so that
  a standard `~/.pypirc` is honored.

## [0.9.1] - 2026-04-08

### Fixed

- Git passthrough log line demoted from INFO to DEBUG to quiet normal use.

## [0.9.0] - 2026-04-07

### Added

- `fzf` subcommand: interactive picker that prints selected paths to stdout,
  usable in pipelines (`d. fzf | xargs ...`).
- `history` subcommand: browse a file's git log and diff any two versions.
- Submodule file support: `list_all` walks submodules at depth=2 so pickers
  (edit/fzf/clip/grep/ls/export/history) include submodule files.
- `CONTRIBUTING.md` documenting the Repository → Action → Protocol pattern
  and the "Adding a New Subcommand" recipe.
- `scripts/` directory with `venv-create.sh`, `test.sh`, `test-watch.sh`,
  `build.sh`, `bump.sh` (replaces the old `tools.sh`).
- Test suite covering actions, editor discovery, clipper discovery,
  repository properties, cache invalidation, and submodule listing.

### Changed

- Migrated from `bump2version` to `bump-my-version`; config moved from
  `.bumpversion.cfg` to `.bumpversion.toml`.
- Protocol classes (`Editor`, `Clipper`, `Actions`) use `...` instead of
  `raise NotImplementedError` in method bodies.
- Action constructors renamed `src_repo` → `repo` for consistency.
- `freshen()` simplified to a `__dict__.pop()` loop.
- `grep` now passes the search term as a string (not list) to the editor.
- Removed unused dev deps: `ipdb`, `pynvim`, `asciinema`.
- Dropped stale TODO comments and ASCII art from source.

### Fixed

- Guard clauses in `Restore` and `DiscardChanges` when fzf returns nothing.
- `list_all` no longer shadows the builtin `all`.

## [0.8.0] - 2025-08-04

### Changed

- **Breaking**: reworked CLI — subcommands replace the long flag form
  (e.g. `d. ls` instead of `d. --list`). `d. list` renamed to `d. ls`.

## [0.7.1] - 2023-09-06

### Changed

- README cleanup pass.

## [0.7.0] - 2023-08-31

### Changed

- Minor version bump (no user-visible changes of note).

## [0.6.1] - 2022-02-08

### Fixed

- `--export` archived the `$DOTFILES` repo with an absolute path, so
  expanding the tarball in `$HOME` landed the repo at
  `$HOME/home/<user>/...` instead of `$HOME/...`. Now stored relative.

## [0.6.0] - 2022-02-02

### Added

- `--export` command: tarball of all tracked files plus the bare
  `$DOTFILES` repo, suitable for bootstrapping a new `$HOME`
  (replaces `--tar`).

## [0.5.0] - 2021-09-30

### Added

- `--clip` option to throw put file paths into the clipboard

## [0.4.0 ] - 2021-09-27

### Added

- `--discard` option to throw away changes in the work-tree

## [0.3.8] - 2021-09-25

### Added

- This changelog.

### Changed

- Changed the logic of how I parse `git status -s --porecelain` renamed files

### Fixed

- A bug caused when a file was both renamed and modified. These files were 
incorrectly parsed by various selectors. I fixed the bug and added regression 
tests to ensure future functionality.

