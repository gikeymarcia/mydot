"""Pilot tests for the `d. watch` Textual TUI."""
import asyncio

import pytest

from mydot.watch import FileItem, WatchApp
from mydot.config import WatchConfig


def _run(coro):
    return asyncio.run(coro)


def _modify(clean_repo, name="fileA", text="changed\n"):
    (clean_repo["worktree"] / name).write_text(text)


def _stage_modify(clean_repo, name="fileA", text="staged\n"):
    f = clean_repo["worktree"] / name
    f.write_text(text)
    clean_repo["git"]("add", str(f))


def test_app_lists_unstaged_file(clean_repo):
    _modify(clean_repo)

    async def scenario():
        app = WatchApp(clean_repo["df"], config=WatchConfig(), poll_seconds=0)
        async with app.run_test() as pilot:
            await pilot.pause()
            items = [c for c in app.query("ListView > FileItem").results(FileItem)]
            assert any(it.path == "fileA" and not it.staged for it in items)

    _run(scenario())


def test_stage_keybinding(clean_repo):
    _modify(clean_repo)

    async def scenario():
        app = WatchApp(clean_repo["df"], config=WatchConfig(), poll_seconds=0)
        async with app.run_test() as pilot:
            await pilot.pause()
            await pilot.press("s")
            await pilot.pause()
            clean_repo["df"].freshen()
            assert "fileA" in clean_repo["df"].modified_staged

    _run(scenario())


def test_unstage_keybinding(clean_repo):
    _stage_modify(clean_repo)

    async def scenario():
        app = WatchApp(clean_repo["df"], config=WatchConfig(), poll_seconds=0)
        async with app.run_test() as pilot:
            await pilot.pause()
            await pilot.press("u")
            await pilot.pause()
            clean_repo["df"].freshen()
            assert "fileA" not in clean_repo["df"].modified_staged
            assert "fileA" in clean_repo["df"].modified_unstaged

    _run(scenario())


def test_j_k_navigation(clean_repo):
    for name in ["fileA", "fileB", "fileC"]:
        (clean_repo["worktree"] / name).write_text(f"edit-{name}\n")

    async def scenario():
        app = WatchApp(clean_repo["df"], config=WatchConfig(), poll_seconds=0)
        async with app.run_test() as pilot:
            await pilot.pause()
            lv = app.query_one("#file_picker")
            start = lv.index
            await pilot.press("j")
            await pilot.pause()
            assert lv.index == (start or 0) + 1
            await pilot.press("k")
            await pilot.pause()
            assert lv.index == (start or 0)

    _run(scenario())


def test_title_uses_config(clean_repo):
    clean_repo["git"]("remote", "add", "origin", "git@example.com:me/dots.git")
    _modify(clean_repo)

    async def scenario():
        cfg = WatchConfig(title_format="WATCH[{branch}|{remote}]")
        app = WatchApp(clean_repo["df"], config=cfg, poll_seconds=0)
        async with app.run_test() as pilot:
            await pilot.pause()
            assert "WATCH[" in app.title
            assert "git@example.com:me/dots.git" in app.title

    _run(scenario())


def test_default_title_omits_remote_when_absent(clean_repo):
    _modify(clean_repo)

    async def scenario():
        app = WatchApp(clean_repo["df"], config=WatchConfig(), poll_seconds=0)
        async with app.run_test() as pilot:
            await pilot.pause()
            assert "mydot" in app.title
            # No remote set on clean_repo, so no parenthetical
            assert "(" not in app.title

    _run(scenario())


def test_default_title_shows_remote_when_present(clean_repo):
    clean_repo["git"]("remote", "add", "origin", "git@example.com:me/dots.git")
    _modify(clean_repo)

    async def scenario():
        app = WatchApp(clean_repo["df"], config=WatchConfig(), poll_seconds=0)
        async with app.run_test() as pilot:
            await pilot.pause()
            assert "(git@example.com:me/dots.git)" in app.title

    _run(scenario())


def test_commit_aborts_when_nothing_staged(clean_repo, monkeypatch):
    """`c` with no staged changes notifies and does not invoke git commit."""
    from mydot.repository import Repository
    called = []
    monkeypatch.setattr(
        Repository, "commit_interactive",
        lambda self: called.append(1) or None,
    )

    async def scenario():
        app = WatchApp(clean_repo["df"], config=WatchConfig(), poll_seconds=0)
        async with app.run_test() as pilot:
            await pilot.pause()
            await pilot.press("c")
            await pilot.pause()
            assert called == []

    _run(scenario())


def test_commit_flow_invokes_git_commit(clean_repo, monkeypatch):
    """`c` suspends the TUI and delegates to `git commit` so user .gitconfig
    (commit.template, commit.verbose, hooks, etc.) is honored."""
    _stage_modify(clean_repo)

    from contextlib import contextmanager
    from mydot.repository import Repository
    import subprocess

    calls = []

    def fake_commit(self):
        calls.append("commit_interactive")
        # Simulate git's editor flow having captured a message.
        return subprocess.run(
            self._git_base + ["commit", "-m", "watch tui commit"],
            text=True, capture_output=True,
        )

    @contextmanager
    def fake_suspend(self):
        yield

    monkeypatch.setattr(WatchApp, "suspend", fake_suspend)
    monkeypatch.setattr(Repository, "commit_interactive", fake_commit)

    async def scenario():
        app = WatchApp(clean_repo["df"], config=WatchConfig(), poll_seconds=0)
        async with app.run_test() as pilot:
            await pilot.pause()
            await pilot.press("c")
            await pilot.pause()
            assert calls == ["commit_interactive"]
            log = clean_repo["git"]("log", "--oneline", "-1").stdout
            assert "watch tui commit" in log

    _run(scenario())



def test_selector_falls_back_when_nerd_fonts_off(clean_repo):
    """With nerd_fonts=False, the highlighted row uses the ASCII fallback `>`."""
    _modify(clean_repo)

    async def scenario():
        from mydot.watch import SELECTOR_PLAIN, FileItem
        cfg = WatchConfig(nerd_fonts=False)
        app = WatchApp(clean_repo["df"], config=cfg, poll_seconds=0)
        async with app.run_test() as pilot:
            await pilot.pause()
            items = list(app.query("ListView > FileItem").results(FileItem))
            assert items, "expected at least one row"
            assert items[0]._selector == SELECTOR_PLAIN
            assert items[0]._row_text(highlighted=True).plain.startswith(SELECTOR_PLAIN)

    _run(scenario())


def test_selector_uses_nerd_glyph_by_default(clean_repo):
    _modify(clean_repo)

    async def scenario():
        from mydot.watch import SELECTOR_NERD, FileItem
        app = WatchApp(clean_repo["df"], config=WatchConfig(), poll_seconds=0)
        async with app.run_test() as pilot:
            await pilot.pause()
            items = list(app.query("ListView > FileItem").results(FileItem))
            assert items
            assert items[0]._selector == SELECTOR_NERD
            assert items[0]._row_text(highlighted=True).plain.startswith(SELECTOR_NERD)

    _run(scenario())



def test_staging_preserves_row_order(clean_repo):
    """Toggling stage state must not shuffle the row order — paths sorted
    alphabetically regardless of staged/unstaged."""
    # clean_repo tracks fileA/B/C — modify all three so they show up.
    for name in ["fileA", "fileB", "fileC"]:
        (clean_repo["worktree"] / name).write_text(f"edit-{name}\n")

    async def scenario():
        from mydot.watch import FileItem
        app = WatchApp(clean_repo["df"], config=WatchConfig(), poll_seconds=0)
        async with app.run_test() as pilot:
            await pilot.pause()
            before = [c.path for c in app.query("ListView > FileItem").results(FileItem)]
            assert before == ["fileA", "fileB", "fileC"]
            # Stage the middle file
            lv = app.query_one("#file_picker")
            lv.index = 1  # fileB
            await pilot.pause()
            await pilot.press("s")
            await pilot.pause()
            after = [c.path for c in app.query("ListView > FileItem").results(FileItem)]
            assert after == ["fileA", "fileB", "fileC"], "order shifted on stage"
            # fileB should now be staged (green) while others remain unstaged
            states = {c.path: c.staged for c in app.query("ListView > FileItem").results(FileItem)}
            assert states == {"fileA": False, "fileB": True, "fileC": False}

    _run(scenario())



def test_partial_stage_shows_partial_state(clean_repo):
    """Stage a change, then modify again — file is in git \"MM\" status.
    Row should be in `partial` state, red-classed, with the green
    `[partially staged]` suffix."""
    f = clean_repo["worktree"] / "fileA"
    f.write_text("v2\n")
    clean_repo["git"]("add", "fileA")
    f.write_text("v3\n")  # further edit after staging

    async def scenario():
        from mydot.watch import FileItem
        app = WatchApp(clean_repo["df"], config=WatchConfig(), poll_seconds=0)
        async with app.run_test() as pilot:
            await pilot.pause()
            items = list(app.query("ListView > FileItem").results(FileItem))
            assert len(items) == 1
            it = items[0]
            assert it.state == "partial"
            assert not it.staged  # back-compat bool: only True when fully staged
            assert "unstaged" in it.classes  # rendered red
            assert "[partially staged]" in it._row_text(highlighted=False).plain

    _run(scenario())


def test_partial_stage_to_fully_staged(clean_repo):
    """Press `s` on a partial row → remaining worktree changes get staged →
    state flips to `staged`."""
    f = clean_repo["worktree"] / "fileA"
    f.write_text("v2\n")
    clean_repo["git"]("add", "fileA")
    f.write_text("v3\n")

    async def scenario():
        from mydot.watch import FileItem
        app = WatchApp(clean_repo["df"], config=WatchConfig(), poll_seconds=0)
        async with app.run_test() as pilot:
            await pilot.pause()
            await pilot.press("s")
            await pilot.pause()
            items = list(app.query("ListView > FileItem").results(FileItem))
            assert len(items) == 1
            assert items[0].state == "staged"

    _run(scenario())



def test_space_toggle_stage_cycle(clean_repo):
    """space stages, then unstages."""
    _modify(clean_repo)

    async def scenario():
        from mydot.watch import FileItem
        app = WatchApp(clean_repo["df"], config=WatchConfig(), poll_seconds=0)
        async with app.run_test() as pilot:
            await pilot.pause()
            assert app.query("FileItem").results(FileItem).__next__().state == "unstaged"
            await pilot.press("space")
            await pilot.pause()
            assert app.query("FileItem").results(FileItem).__next__().state == "staged"
            await pilot.press("space")
            await pilot.pause()
            assert app.query("FileItem").results(FileItem).__next__().state == "unstaged"

    _run(scenario())


def test_yank_calls_clipper(clean_repo, monkeypatch):
    """`yy` invokes the same find_clipper chain as `d. clip`."""
    _modify(clean_repo)

    clipped = []

    class FakeClipper:
        name = "fake"
        def clip(self, data): clipped.append(data)

    monkeypatch.setattr("mydot.watch.find_clipper", lambda: FakeClipper())

    async def scenario():
        app = WatchApp(clean_repo["df"], config=WatchConfig(), poll_seconds=0)
        async with app.run_test() as pilot:
            await pilot.pause()
            await pilot.press("y")
            await pilot.press("y")
            await pilot.pause()
            assert clipped, "clipper not invoked"
            assert clipped[0].endswith("/fileA")
            assert clipped[0].startswith("/")  # absolute path

    _run(scenario())


def test_single_y_does_not_yank(clean_repo, monkeypatch):
    """Single `y` must NOT yank — needs `yy` like vim."""
    _modify(clean_repo)
    clipped = []
    class FakeClipper:
        name = "fake"
        def clip(self, data): clipped.append(data)
    monkeypatch.setattr("mydot.watch.find_clipper", lambda: FakeClipper())

    async def scenario():
        import asyncio
        app = WatchApp(clean_repo["df"], config=WatchConfig(), poll_seconds=0)
        async with app.run_test() as pilot:
            await pilot.pause()
            await pilot.press("y")
            await asyncio.sleep(0.6)  # let the 500ms timeout expire
            assert clipped == []

    _run(scenario())


def test_edit_invokes_editor(clean_repo, monkeypatch):
    """`e` calls editor.open with the absolute path."""
    _modify(clean_repo)

    opened = []

    class FakeEditor:
        program = "fake"
        def open(self, files, search=None): opened.extend(files)

    monkeypatch.setattr("mydot.watch.find_editor", lambda: FakeEditor())

    from contextlib import contextmanager
    @contextmanager
    def fake_suspend(self): yield
    monkeypatch.setattr(WatchApp, "suspend", fake_suspend)

    async def scenario():
        app = WatchApp(clean_repo["df"], config=WatchConfig(), poll_seconds=0)
        async with app.run_test() as pilot:
            await pilot.pause()
            await pilot.press("e")
            await pilot.pause()
            assert opened, "editor not invoked"
            assert str(opened[0]).endswith("/fileA")

    _run(scenario())


def test_jump_top_bottom(clean_repo):
    """G jumps to bottom, gg jumps back to top."""
    for name in ["fileA", "fileB", "fileC"]:
        (clean_repo["worktree"] / name).write_text(f"v2-{name}\n")

    async def scenario():
        app = WatchApp(clean_repo["df"], config=WatchConfig(), poll_seconds=0)
        async with app.run_test() as pilot:
            await pilot.pause()
            lv = app.query_one("#file_picker")
            assert lv.index == 0
            await pilot.press("G")
            await pilot.pause()
            assert lv.index == 2
            await pilot.press("g")
            await pilot.press("g")
            await pilot.pause()
            assert lv.index == 0

    _run(scenario())


def test_help_screen_opens(clean_repo):
    _modify(clean_repo)

    async def scenario():
        from mydot.watch import HelpScreen
        app = WatchApp(clean_repo["df"], config=WatchConfig(), poll_seconds=0)
        async with app.run_test() as pilot:
            await pilot.pause()
            await pilot.press("question_mark")
            await pilot.pause()
            assert isinstance(app.screen, HelpScreen)
            await pilot.press("escape")
            await pilot.pause()
            assert not isinstance(app.screen, HelpScreen)

    _run(scenario())


def test_tab_cycles_focus(clean_repo):
    _modify(clean_repo)

    async def scenario():
        app = WatchApp(clean_repo["df"], config=WatchConfig(), poll_seconds=0)
        async with app.run_test() as pilot:
            await pilot.pause()
            left = app.query_one("#file_picker")
            right = app.query_one("#preview")
            # Whichever pane starts focused, tab should switch
            initial = app.focused
            await pilot.press("tab")
            await pilot.pause()
            assert app.focused is not initial
            assert app.focused in (left, right)

    _run(scenario())



def test_j_k_routes_to_focused_pane(clean_repo):
    """When right pane has focus, j/k must scroll the diff, NOT move the
    file-list cursor."""
    for name in ["fileA", "fileB"]:
        (clean_repo["worktree"] / name).write_text(f"v2-{name}\n")

    async def scenario():
        app = WatchApp(clean_repo["df"], config=WatchConfig(), poll_seconds=0)
        async with app.run_test() as pilot:
            await pilot.pause()
            lv = app.query_one("#file_picker")
            assert lv.index == 0
            # Tab to right pane
            await pilot.press("tab")
            await pilot.pause()
            # j should not move the file cursor now
            await pilot.press("j")
            await pilot.pause()
            assert lv.index == 0, "j moved file cursor while right pane was focused"
            # Tab back; j should resume moving the cursor
            await pilot.press("tab")
            await pilot.pause()
            await pilot.press("j")
            await pilot.pause()
            assert lv.index == 1

    _run(scenario())
