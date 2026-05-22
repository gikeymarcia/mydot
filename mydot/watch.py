"""Lazygit-style TUI for browsing/staging dotfile changes."""
from __future__ import annotations

from typing import Optional

from pathlib import Path

from rich.text import Text
from textual.app import App, ComposeResult
from textual.binding import Binding
from textual.containers import Center, Horizontal, VerticalScroll
from textual.screen import ModalScreen
from textual.widgets import Footer, Header, Label, ListItem, ListView, Static

from mydot.clip import find_clipper
from mydot.config import WatchConfig, load_watch_config
from mydot.editor import find_editor
from mydot.repository import Repository


SELECTOR_NERD  = ""  # nf-oct-arrow_right (U+F432)
SELECTOR_PLAIN = ">"       # ASCII fallback when nerd_fonts = false


# State of a file in the working tree:
#   "unstaged" — modifications in worktree, nothing staged
#   "staged"   — staged, no further worktree edits since
#   "partial"  — staged + further worktree edits (git "MM" status)
FileState = str
STATUS_MARKERS = {"staged": "●", "partial": "◐", "unstaged": "○"}


class FileItem(ListItem):
    def __init__(self, path: str, state: FileState, selector: str = SELECTOR_NERD) -> None:
        self.path = path
        self.state = state
        # back-compat: tests use .staged as a bool
        self.staged = state == "staged"
        self._selector = selector
        self._status_marker = STATUS_MARKERS[state]
        self._label = Label(self._row_text(highlighted=False))
        super().__init__(self._label)
        # Color class: partial files render in unstaged-red because there
        # are still uncommitted edits in the worktree; the green suffix
        # tells you part of the file is staged.
        self.add_class("staged" if state == "staged" else "unstaged")

    def _row_text(self, highlighted: bool):
        # Selector and the un-highlighted placeholder each occupy one cell —
        # modern terminals (Ghostty/Kitty/WezTerm) render Nerd Font private-
        # use glyphs as single-width, so we don't pad.
        prefix = self._selector if highlighted else " "
        text = Text(f"{prefix} {self._status_marker} {self.path}")
        if self.state == "partial":
            text.append(" [partially staged]", style="bold green")
        return text

    def set_highlighted(self, highlighted: bool) -> None:
        self._label.update(self._row_text(highlighted))


class WatchApp(App):
    # Palette comes from whatever Textual theme is active (Ctrl+P → Change
    # theme). $error / $success / $surface / $accent are all theme-defined.
    # Backgrounds set to `transparent` (alpha 0) so Textual omits the cell
    # bg SGR code → terminal transparency shows through. The highlight row
    # keeps a solid bg so the selection stays legible.
    CSS = """
    Screen { background: transparent; layout: vertical; }
    #body  { background: transparent; height: 1fr; }
    #file_picker, #preview { background: transparent; }
    #file_picker  { width: 40%; border: solid $surface-lighten-2; }
    #preview { width: 60%; border: solid $surface-lighten-2; }
    #file_picker:focus-within  { border: solid $accent; }
    #preview:focus-within { border: solid $accent; }
    #diff  { background: transparent; padding: 0 1; }
    ListView, ListItem { background: transparent; }
    ListItem.unstaged > Label { background: transparent; color: $error;   text-style: bold; }
    ListItem.staged   > Label { background: transparent; color: $success; text-style: bold; }
    /* No --highlight bg: alpha compositing fights terminal transparency.
       Selection cue is the nerd-font caret prefix injected by FileItem. */
    Header { background: transparent; }
    Footer { background: transparent; }
    """

    BINDINGS = [
        Binding("j", "cursor_down", "↓", show=False),
        Binding("k", "cursor_up", "↑", show=False),
        Binding("down", "cursor_down", "Down", show=False),
        Binding("up", "cursor_up", "Up", show=False),
        Binding("g", "double_key('g')", "Top (gg)", show=False),
        Binding("G", "jump_bottom", "Bottom", show=False),
        Binding("tab", "focus_next_pane", "↹", show=False),
        Binding("s", "stage", "Stage"),
        Binding("u", "unstage", "Unstage"),
        Binding("space", "toggle_stage", "Toggle"),
        Binding("e", "edit", "Edit"),
        Binding("enter", "edit", "Edit", show=False),
        Binding("y", "double_key('y')", "Yank (yy)", show=False),
        Binding("c", "commit", "Commit"),
        Binding("r", "refresh_now", "Refresh"),
        Binding("question_mark", "help", "Help"),
        Binding("q", "quit", "Quit"),
    ]

    def __init__(
        self,
        repo: Repository,
        config: Optional[WatchConfig] = None,
        poll_seconds: float = 1.0,
    ) -> None:
        # ansi_color=True activates Screen's `&:ansi` pseudo-class so
        # Textual emits `background: ansi_default` for cells with no
        # explicit truecolor bg — which is the only way to let terminal
        # transparency show through.
        super().__init__(ansi_color=True)
        self.repo = repo
        self.cfg = config if config is not None else load_watch_config()
        self.poll_seconds = poll_seconds
        # Two-key sequences (gg, yy) share one pending slot. set_timer
        # clears it after the timeout so a stray `g` or `y` doesn't lurk.
        self._pending_key: Optional[str] = None
        self._pending_timer = None
        self._double_key_actions = {
            "g": self._do_jump_top,
            "y": self._do_yank_path,
        }
        # Apply the user-selected (or default) Textual built-in theme.
        # Ctrl+P → "Change theme" lets users override at runtime.
        try:
            self.theme = self.cfg.theme
        except Exception:
            pass  # unknown theme name; Textual falls back to its default

    def compose(self) -> ComposeResult:
        yield Header(show_clock=False)
        with Horizontal(id="body"):
            yield ListView(id="file_picker")
            with VerticalScroll(id="preview"):
                yield Static(id="diff")
        yield Footer()

    def on_mount(self) -> None:
        self.refresh_title()
        self.populate()
        if self.poll_seconds > 0:
            self.set_interval(self.poll_seconds, self.populate)

    def refresh_title(self) -> None:
        self.title = self.cfg.render_title(
            branch=self.repo.branch_name(),
            remote=self.repo.remote_url(),
        )

    def _gather_items(self) -> list[tuple[str, str]]:
        """Return a stable alphabetically-sorted list. State (staged vs
        unstaged vs partial) only affects color + marker — never row
        position — so toggling stage/unstage doesn't shuffle the cursor."""
        self.repo.freshen()
        unstaged = set(self.repo.modified_unstaged)
        staged = set(self.repo.restorables)
        def state_of(p: str) -> str:
            in_u, in_s = p in unstaged, p in staged
            if in_u and in_s: return "partial"
            if in_s:          return "staged"
            return "unstaged"
        return [(p, state_of(p)) for p in sorted(unstaged | staged)]

    def populate(self) -> None:
        listview = self.query_one("#file_picker", ListView)
        new_items = self._gather_items()

        existing = [
            (c.path, c.state) for c in listview.children if isinstance(c, FileItem)
        ]
        if existing == new_items:
            self.update_diff()
            return

        prior_index = listview.index or 0
        listview.clear()
        selector = SELECTOR_NERD if self.cfg.nerd_fonts else SELECTOR_PLAIN
        for path, state in new_items:
            listview.append(FileItem(path, state=state, selector=selector))
        if new_items:
            listview.index = min(prior_index, len(new_items) - 1)
        self.update_diff()

    def update_diff(self) -> None:
        diff_widget = self.query_one("#diff", Static)
        current = self._current_item()
        # Push selector glyph into the highlighted row, clear it from siblings.
        for child in self.query_one("#file_picker", ListView).children:
            if isinstance(child, FileItem):
                child.set_highlighted(child is current)
        if current is None:
            diff_widget.update(Text("(no changes — working tree clean)"))
            return
        # Partial files show the worktree diff (the unstaged piece).
        raw = self.repo.diff_for(current.path, staged=current.state == "staged", color=True)
        diff_widget.update(Text.from_ansi(raw) if raw else Text("(empty diff)"))

    def _current_item(self) -> Optional[FileItem]:
        item = self.query_one("#file_picker", ListView).highlighted_child
        return item if isinstance(item, FileItem) else None

    def on_list_view_highlighted(self, _: ListView.Highlighted) -> None:
        self.update_diff()

    def action_cursor_down(self) -> None:
        """j / ↓ — routes to whichever pane has focus."""
        if self._right_pane_focused():
            self.query_one("#preview", VerticalScroll).scroll_down(animate=False)
        else:
            self.query_one("#file_picker", ListView).action_cursor_down()

    def action_cursor_up(self) -> None:
        if self._right_pane_focused():
            self.query_one("#preview", VerticalScroll).scroll_up(animate=False)
        else:
            self.query_one("#file_picker", ListView).action_cursor_up()

    def _right_pane_focused(self) -> bool:
        right = self.query_one("#preview", VerticalScroll)
        f = self.focused
        while f is not None:
            if f is right:
                return True
            f = f.parent
        return False

    def action_stage(self) -> None:
        item = self._current_item()
        # Partial → stage the remaining worktree changes; unstaged → stage all.
        if item and item.state != "staged":
            self.repo.stage(item.path)
            self.populate()

    def action_unstage(self) -> None:
        item = self._current_item()
        if item and item.state != "unstaged":
            self.repo.unstage(item.path)
            self.populate()

    def action_refresh_now(self) -> None:
        self.refresh_title()
        self.populate()

    # ---- vim-style two-key sequences (gg, yy) -----------------------

    def action_double_key(self, key: str) -> None:
        """First press arms a 500ms timer for `key`; second press within
        the window fires the registered action."""
        if self._pending_key == key:
            self._clear_pending_key()
            action = self._double_key_actions.get(key)
            if action is not None:
                action()
        else:
            self._pending_key = key
            self._pending_timer = self.set_timer(0.5, self._clear_pending_key)

    def _clear_pending_key(self) -> None:
        self._pending_key = None
        if self._pending_timer is not None:
            try: self._pending_timer.stop()
            except Exception: pass
            self._pending_timer = None

    def _do_jump_top(self) -> None:
        if self._right_pane_focused():
            self.query_one("#preview", VerticalScroll).scroll_home(animate=False)
            return
        lv = self.query_one("#file_picker", ListView)
        if list(lv.children):
            lv.index = 0

    def _do_yank_path(self) -> None:
        """yy: copy the file's absolute path to the clipboard using the
        same `find_clipper()` chain as `d. clip` (wl-copy → xclip → xsel
        → pbcopy → fallback)."""
        item = self._current_item()
        if not item:
            return
        abs_path = str((Path(self.repo.work_tree) / item.path).absolute())
        find_clipper().clip(abs_path)
        self.notify(f"Copied: {abs_path}")

    def action_jump_bottom(self) -> None:
        if self._right_pane_focused():
            self.query_one("#preview", VerticalScroll).scroll_end(animate=False)
            return
        lv = self.query_one("#file_picker", ListView)
        n = len(list(lv.children))
        if n:
            lv.index = n - 1

    def action_focus_next_pane(self) -> None:
        right = self.query_one("#preview", VerticalScroll)
        left = self.query_one("#file_picker", ListView)
        if self.focused is left:
            right.focus()
        else:
            left.focus()

    # ---- file actions reusing CLI infra -----------------------------

    def action_toggle_stage(self) -> None:
        """Space: stage if not fully staged, otherwise unstage."""
        item = self._current_item()
        if not item:
            return
        if item.state == "staged":
            self.repo.unstage(item.path)
        else:
            self.repo.stage(item.path)
        self.populate()

    def action_edit(self) -> None:
        """`e` / Enter: open file in $EDITOR via the same `find_editor()`
        discovery used by `d. edit`. Suspends TUI so the editor owns the TTY."""
        item = self._current_item()
        if not item:
            return
        abs_path = Path(self.repo.work_tree) / item.path
        editor = find_editor()
        with self.suspend():
            editor.open([abs_path.absolute()])
        self.populate()

    def action_help(self) -> None:
        self.push_screen(HelpScreen())

    def action_commit(self) -> None:
        self.repo.freshen()
        if not self.repo.restorables:
            self.notify("Nothing staged to commit.", severity="warning")
            return
        with self.suspend():
            result = self.repo.commit_interactive()
        if result.returncode == 0:
            self.notify("Commit recorded.")
            self.refresh_title()
        else:
            self.notify(
                "Commit aborted (empty message or hook rejection).",
                severity="warning",
            )
        self.populate()


HELP_TEXT = """\
[b]Navigation[/b]
  j / ↓        cursor down
  k / ↑        cursor up
  gg           jump to top
  G            jump to bottom
  tab          toggle focus (list ↔ diff pane)

[b]Staging[/b]
  s            stage
  u            unstage
  space        toggle stage state

[b]File ops[/b]
  e / enter    open in $EDITOR (same chain as `d. edit`)
  yy           yank absolute path to clipboard (same chain as `d. clip`)

[b]Commit[/b]
  c            git commit (uses your full .gitconfig editor flow)

[b]Misc[/b]
  r            refresh now
  ?            this help
  q            quit

[b]Theme[/b]
  Ctrl+P → "Change theme"   (Textual built-in palette)
"""


class HelpScreen(ModalScreen):
    BINDINGS = [
        Binding("escape", "app.pop_screen", "Close"),
        Binding("q",      "app.pop_screen", "Close"),
        Binding("question_mark", "app.pop_screen", "Close"),
    ]
    CSS = """
    HelpScreen { align: center middle; background: $background 70%; }
    #help-box  { width: 60; height: auto; padding: 1 2; border: thick $accent; background: $surface; }
    """

    def compose(self) -> ComposeResult:
        with Center(id="help-box"):
            yield Static(HELP_TEXT)


def run_watch(repo: Repository) -> None:
    WatchApp(repo).run()
