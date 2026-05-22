## Handoff — mydot post-0.13.0 (just merged + published)

### State at handoff

- **PyPI:** latest published is **0.13.0** (2026-05-22). 0.12.0 (the
  submodule fix) is the prior release.
- Branch: **`master`** post-merge. Commit `01831d4` (the last pre-0.13
  master tip) sits below the squashed `0.13.0` merge commit.
- Tag `v0.13.0` is on master at the merge commit (your step, not Claude's).
- Tests: **137 passing**.
- Worktree should be clean after pickup `git pull`.

### What shipped in 0.13.0 (2026-05-22)

**New `d. watch` lazygit-style Textual TUI** with full keybinding set:

| Category    | Keys                                               |
|-------------|----------------------------------------------------|
| Navigation  | `j`/`k`/`↑`/`↓`, `gg`/`G`, `tab`                   |
| Staging     | `s`, `u`, `space` (toggle)                         |
| File ops    | `e`/`enter` (editor), `yy` (yank path)             |
| Commit      | `c`                                                |
| Misc        | `r` (refresh), `?` (help), `q` (quit)              |

- Two-pane layout: `#file_picker` (left, file list) + `#preview` (right,
  colored diff). `j`/`k`/`gg`/`G` route to whichever pane has focus
  (`tab` to switch).
- Three file states with distinct markers and colors:
  - `○` unstaged   — red
  - `●` staged     — green
  - `◐` partial    — red with green `[partially staged]` suffix (git "MM")
- Row order is alphabetically stable; staging never shuffles the cursor.
- Title shows the active branch with a Nerd Font branch glyph
  (`nf-oct-git_branch`). Remote URL appended in parens only when one is
  configured.
- Selection cue is a Nerd Font caret (`nf-oct-arrow_right`) in front of
  the highlighted row — no highlight-row bg (alpha fights terminal
  transparency).
- 1s poll on `git status` so the TUI stays current while editing files
  in another pane.

**Config** — `~/.config/mydot/config.ini`:

```ini
[watch]
theme        = catppuccin-mocha          ; any Textual built-in theme
nerd_fonts   = true                      ; false → drop glyph, use ">" selector
title_format = mydot --  {branch}{remote_suffix}
```

Placeholders: `{branch}`, `{remote}`, `{remote_suffix}` (auto-expands to
`" ({remote})"` when present, empty otherwise).

**Commit flow** — `c` calls `App.suspend()` and shells to plain `git
commit` (no `-F`, no `-m`) so the user's full `.gitconfig` editor path
runs: `commit.template`, `commit.verbose`, `commit.cleanup`,
prepare-commit-msg/commit-msg hooks, GPG signing with TTY passphrase,
aliases.

**Repository helpers added**: `branch_name`, `remote_url`, `diff_for`,
`stage`, `unstage`, `commit_interactive`.

**Reuses existing CLI infra**: `find_editor()` (for `e`), `find_clipper()`
(for `yy`) — same chains as `d. edit` and `d. clip`.

**User-facing docs**: `docs/watch.md` — full reference with layout,
keybindings, states, config, themes, transparency, contrast notes.
Linked from README.

**New runtime dep**: `textual>=0.50` (added to `setup.py`).

### Decisions made in 0.13.0 and *why*

1. **Textual themes over a homegrown theme INI system.** First cut shipped
   `mydot/themes/*.ini` + a `Theme` dataclass + `get_css_variables` override.
   Textual already does this via Ctrl+P. Ripped out ~150 lines; CSS now
   uses `$error`/`$success`/`$surface-lighten-1`/`$accent` straight from
   the active Textual theme. Default theme name is the only knob in
   `config.ini`.

2. **Highlight bg held constant; focus shown via container border.**
   Verified ratios with `wcag-contrast-ratio`: brighter highlight bgs
   sink the red below WCAG AA-large (3:1). Focus is indicated by the
   container border color (`$surface-lighten-2` → `$accent` on
   `:focus-within`), not by brightening the row.

3. **1s poll over fs-watcher.** Bare repo + `$HOME` work-tree means
   recursive inotify would watch `~/.cache`, browser profiles, etc. —
   fights `fs.inotify.max_user_watches` for no benefit. `git status
   --porcelain` on the index is sub-50ms for hundreds of tracked files.

4. **`git commit` (no `-F`) over our own editor flow.** Letting git
   invoke `$GIT_EDITOR` itself is the only way to honor user
   `.gitconfig` editor-path config. Suspending Textual frees the TTY
   for GPG / interactive prompts.

5. **`ansi_color=True` on the Textual App for terminal transparency.**
   Activates Screen's `&:ansi` pseudo-class so cells without an explicit
   truecolor background emit `ansi_default` (no SGR `48;…` code) → the
   terminal's own bg shines through. Tested on Ghostty and Kitty.

6. **Stable alphabetical row order across stage toggles.** State only
   affects color + marker. Partial-stage (file in both unstaged and
   staged sets) gets the `partial` state instead of an ambiguous
   staged-or-not call.

7. **Two-key sequences (`gg`, `yy`) share one `_pending_key` slot.**
   First press arms a 500ms timer; second press fires the registered
   action. One state machine + `_double_key_actions` dict; easy to add
   `dd`/`xx` later by appending one entry.

8. **`#file_picker` / `#preview` IDs over `#left` / `#right`.** Opaque
   positional names leaked into 20+ action methods; descriptive names
   self-document the routing logic.

9. **Dropped `commit_from_file` helper.** Was only kept to make two
   tests easier to write; live commit path uses `commit_interactive()`.
   Pure dead code, deleted along with its tests.

10. **Considered + rejected: widening `Repository.stage`/`unstage` to
    variadic with verbose + auto-`freshen`** so existing fzf-picker
    actions could route through them. Helper would need capture-toggle,
    variadic args, hidden `freshen()` — more cognitive load than the
    three one-liners it would replace. Drift risk is theoretical.

### Outstanding (`docs/TODO.md`)

- Replace `python -m mydot` usage hints with `d.` — it's the alias
  everyone actually uses. Touches `mydot/__main__.py` argparse `prog`,
  `docs/watch.md`, `docs/ideas.md`, `docs/bugs/0001 - Fix incompatible
  type hint.md`. Added in 0.13.0 session, not yet picked up.
- Make `d. history` work for submodule files (query the inner repo's
  own git log).
- Record asciinema demos for each subcommand.

### Carried-forward "next time" items (not bugs)

- Action classes with only `self.repo` + `run()` could be functions.
- `sys.exit()` as flow control makes cancel paths hard to test/compose.
- Submodule conftest fixtures largely duplicate each other; a builder
  pattern would make them declarative.
- `__main__.py` match/case dispatch (13 commands now with `watch`) — a
  registry dict would remove the per-command edit.
- `Repository` mixes data object + subprocess runner — a thin
  `GitClient` would separate concerns.

### How to come back up

1. `git checkout master && git pull` — pickup at the post-merge tip.
2. `bash scripts/venv-create.sh` to recreate `.venv/`.
3. `bash scripts/test.sh` — expect **137 passing**.
4. `d. watch` to dogfood; `?` for the help modal.
5. Pick a TODO and cut a fresh feature branch from master.
