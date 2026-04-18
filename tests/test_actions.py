import os
import subprocess as sp
import tarfile
from pathlib import Path
from unittest.mock import patch, MagicMock, call

import pytest

import mydot
from mydot.actions import (
    AddChanges,
    ChangeDir,
    DiscardChanges,
    FzfSelector,
    GitPassthrough,
    Grep,
    History,
    Restore,
)


# -- Guard clause tests --


def test_restore_exits_when_nothing_staged(clean_repo):
    """Restore.run() should sys.exit when restorables is empty."""
    dotfiles = clean_repo["df"]
    assert dotfiles.restorables == []
    action = Restore(dotfiles)
    with pytest.raises(SystemExit):
        action.run()


def test_discard_exits_when_nothing_unstaged(clean_repo):
    """DiscardChanges.run() should sys.exit when nothing is unstaged."""
    dotfiles = clean_repo["df"]
    assert dotfiles.modified_unstaged == []
    action = DiscardChanges(dotfiles)
    with pytest.raises(SystemExit):
        action.run()


def test_add_exits_when_nothing_unstaged(clean_repo):
    """AddChanges.run() should sys.exit when nothing to add."""
    dotfiles = clean_repo["df"]
    action = AddChanges(dotfiles)
    with pytest.raises(SystemExit):
        action.run()


# -- Grep.join_args tests --


def test_grep_join_args_plain(clean_repo):
    grep = Grep(clean_repo["df"], ["TODO"])
    assert grep.joined == " TODO"


def test_grep_join_args_pipe_gets_quoted(clean_repo):
    grep = Grep(clean_repo["df"], ["foo|bar"])
    assert grep.joined == " 'foo|bar'"


def test_grep_join_args_mixed(clean_repo):
    grep = Grep(clean_repo["df"], ["-i", "foo|bar", "baz"])
    assert grep.joined == " -i 'foo|bar' baz"


def test_grep_join_args_multiple_plain(clean_repo):
    grep = Grep(clean_repo["df"], ["-n", "-i", "pattern"])
    assert grep.joined == " -n -i pattern"


# -- Grep search= passed to editor --


def test_grep_passes_pattern_string_to_editor(clean_repo):
    """Grep.run() should pass search as a str, not a list."""
    dotfiles = clean_repo["df"]
    worktree = clean_repo["worktree"]
    # Create a file with searchable content
    (worktree / "fileA").write_text("TODO fix this\n")

    mock_editor = MagicMock()
    grep = Grep(dotfiles, ["TODO"])

    with patch("pydymenu.fzf", return_value=["fileA"]), \
         patch("mydot.actions.find_editor", return_value=mock_editor):
        grep.run()

    mock_editor.open.assert_called_once()
    _, kwargs = mock_editor.open.call_args
    assert isinstance(kwargs["search"], str)
    assert kwargs["search"] == "TODO"


def test_grep_passes_last_arg_as_search(clean_repo):
    """When regexp includes flags, only the pattern (last arg) goes to the editor."""
    dotfiles = clean_repo["df"]
    worktree = clean_repo["worktree"]
    (worktree / "fileA").write_text("TODO fix this\n")

    mock_editor = MagicMock()
    grep = Grep(dotfiles, ["-i", "TODO"])

    with patch("pydymenu.fzf", return_value=["fileA"]), \
         patch("mydot.actions.find_editor", return_value=mock_editor):
        grep.run()

    _, kwargs = mock_editor.open.call_args
    assert kwargs["search"] == "TODO"


# -- Editor search command integration --


def test_neovim_search_command(tmp_path):
    """Neovim should pass search as /<pattern> to -c flag."""
    from mydot.editor import Neovim

    f = tmp_path / "test.txt"
    f.write_text("hello\n")

    with patch("mydot.editor.subprocess.run") as mock_run:
        Neovim().open([f], search="TODO")

    cmd = mock_run.call_args[0][0]
    assert "-c" in cmd
    assert "/TODO" in cmd
    assert "['TODO']" not in str(cmd)


def test_vim_search_command(tmp_path):
    """Vim should pass search as /<pattern> to -c flag."""
    from mydot.editor import Vim

    f = tmp_path / "test.txt"
    f.write_text("hello\n")

    with patch("mydot.editor.subprocess.run") as mock_run:
        Vim().open([f], search="TODO")

    cmd = mock_run.call_args[0][0]
    assert "-c" in cmd
    assert "/TODO" in cmd


def test_nano_search_command(tmp_path):
    """Nano should pass search as +c/<pattern>."""
    from mydot.editor import Nano

    f = tmp_path / "test.txt"
    f.write_text("hello\n")

    with patch("mydot.editor.subprocess.run") as mock_run:
        Nano().open([f], search="TODO")

    cmd = mock_run.call_args[0][0]
    assert "+c/TODO" in cmd


# -- ExportTar tests --


def test_export_tar_creates_tarball(tmp_path):
    """ExportTar should create a tarball containing tracked files."""
    bare = tmp_path / "worktree" / ".dotrepo"
    worktree = tmp_path / "worktree"
    bare.mkdir(parents=True)
    sp.run(["git", "init", "--bare", bare], capture_output=True)

    def git(*args):
        cmd = ["git", f"--git-dir={bare}", f"--work-tree={worktree}"]
        return sp.run(cmd + list(args), capture_output=True, text=True)

    test_file = worktree / "hello.txt"
    test_file.write_text("hello world\n")
    git("add", str(test_file))
    git("commit", "-m", "init")

    repo = mydot.Repository(bare, worktree)
    from mydot.actions import ExportTar

    action = ExportTar(repo)
    tarball = action.run()

    assert tarball.exists()
    with tarfile.open(tarball) as tf:
        names = tf.getnames()
    assert "hello.txt" in names


# -- GitPassthrough tests --


def test_git_passthrough_runs_command(clean_repo):
    """GitPassthrough should pass args through to git."""
    dotfiles = clean_repo["df"]
    action = GitPassthrough(dotfiles, ["status", "-s"])
    # Should not raise
    action.run()


def test_git_passthrough_restores_directory(clean_repo):
    """GitPassthrough should chdir back to run_from."""
    dotfiles = clean_repo["df"]
    expected_dir = dotfiles.run_from
    action = GitPassthrough(dotfiles, ["branch"])
    action.run()
    assert Path.cwd() == expected_dir


# -- Restore/DiscardChanges with selections via mock --


def test_restore_unstages_files(fake_repo):
    """Restore should unstage selected files when fzf returns a selection."""
    dotfiles = fake_repo["df"]
    restorables = dotfiles.restorables
    assert len(restorables) > 0

    pick = [restorables[0]]
    with patch("pydymenu.fzf", return_value=pick):
        action = Restore(dotfiles)
        action.run()

    assert action.result == pick


def test_discard_restores_files(fake_repo):
    """DiscardChanges should restore selected files when fzf returns a selection."""
    dotfiles = fake_repo["df"]
    unstaged = dotfiles.modified_unstaged
    assert len(unstaged) > 0

    pick = [unstaged[0]]
    with patch("pydymenu.fzf", return_value=pick):
        action = DiscardChanges(dotfiles)
        action.run()

    assert action.result == pick


def test_restore_exits_on_no_selection(fake_repo):
    """Restore should sys.exit when fzf returns None (user cancelled)."""
    dotfiles = fake_repo["df"]
    assert len(dotfiles.restorables) > 0

    with patch("pydymenu.fzf", return_value=None):
        action = Restore(dotfiles)
        with pytest.raises(SystemExit):
            action.run()


def test_discard_exits_on_no_selection(fake_repo):
    """DiscardChanges should sys.exit when fzf returns None."""
    dotfiles = fake_repo["df"]
    assert len(dotfiles.modified_unstaged) > 0

    with patch("pydymenu.fzf", return_value=None):
        action = DiscardChanges(dotfiles)
        with pytest.raises(SystemExit):
            action.run()


# -- FzfSelector tests --


def test_fzf_selector_prints_absolute_paths(clean_repo, capsys):
    """FzfSelector should print absolute paths to stdout."""
    dotfiles = clean_repo["df"]
    worktree = clean_repo["worktree"]

    with patch("pydymenu.fzf", return_value=["fileA", "fileB"]):
        FzfSelector(dotfiles).run()

    output = capsys.readouterr().out.strip().split("\n")
    assert str(worktree / "fileA") in output[0]
    assert str(worktree / "fileB") in output[1]


def test_fzf_selector_exits_on_no_selection(clean_repo):
    """FzfSelector should sys.exit when fzf returns None."""
    dotfiles = clean_repo["df"]

    with patch("pydymenu.fzf", return_value=None):
        with pytest.raises(SystemExit):
            FzfSelector(dotfiles).run()


def test_fzf_selector_returns_paths(clean_repo):
    """FzfSelector.run() should return list of absolute path strings."""
    dotfiles = clean_repo["df"]
    worktree = clean_repo["worktree"]

    with patch("pydymenu.fzf", return_value=["fileA"]):
        result = FzfSelector(dotfiles).run()

    assert len(result) == 1
    assert result[0] == str((worktree / "fileA").resolve())


# -- History tests --


def test_history_exits_on_no_file_selection(clean_repo):
    """History should sys.exit when no file is selected."""
    dotfiles = clean_repo["df"]
    mock_editor = MagicMock()

    with patch("pydymenu.fzf", return_value=None):
        with pytest.raises(SystemExit):
            History(dotfiles, editor=mock_editor).run()


def test_history_exits_on_empty_log(clean_repo):
    """History should sys.exit when the file has no git history."""
    dotfiles = clean_repo["df"]
    mock_editor = MagicMock()

    # fzf returns a file, but git log returns nothing
    with patch("pydymenu.fzf", return_value=["fileA"]), \
         patch("mydot.actions.subprocess.run") as mock_sub:
        mock_sub.return_value = MagicMock(stdout="", returncode=0)
        with pytest.raises(SystemExit):
            History(dotfiles, editor=mock_editor).run()


def test_history_exits_on_no_commit_selection(clean_repo):
    """History should sys.exit when no commit is selected."""
    dotfiles = clean_repo["df"]
    mock_editor = MagicMock()

    # First fzf returns file, second returns None
    fzf_calls = [["fileA"], None]
    with patch("pydymenu.fzf", side_effect=fzf_calls), \
         patch("mydot.actions.subprocess.run") as mock_sub:
        mock_sub.return_value = MagicMock(stdout="abc1234 initial commit\n", returncode=0)
        with pytest.raises(SystemExit):
            History(dotfiles, editor=mock_editor).run()


def test_history_opens_current_and_old_in_editor(fake_repo):
    """History should open current file and temp file with old version in editor."""
    dotfiles = fake_repo["df"]
    mock_editor = MagicMock()

    # Need a file with real git history
    tracked = dotfiles.tracked
    assert len(tracked) > 0
    target = tracked[0]

    # Get a real commit hash
    log = sp.run(
        dotfiles._git_base + ["log", "--oneline", "--", target],
        capture_output=True, text=True,
    )
    commit_line = log.stdout.strip().split("\n")[0]

    fzf_calls = [[target], [commit_line]]
    with patch("pydymenu.fzf", side_effect=fzf_calls):
        History(dotfiles, editor=mock_editor).run()

    mock_editor.open.assert_called_once()
    files_opened = mock_editor.open.call_args[0][0]
    assert len(files_opened) == 2
    # First should be the current file (absolute path)
    assert files_opened[0] == Path(target).absolute()
    # Second should be a temp file that exists
    assert files_opened[1].exists()


def test_history_temp_file_has_old_content(fake_repo):
    """The temp file should contain the content from the selected commit."""
    dotfiles = fake_repo["df"]
    mock_editor = MagicMock()

    tracked = dotfiles.tracked
    target = tracked[0]

    log = sp.run(
        dotfiles._git_base + ["log", "--oneline", "--", target],
        capture_output=True, text=True,
    )
    commit_line = log.stdout.strip().split("\n")[0]
    commit_hash = commit_line.split()[0]

    # Get expected content
    expected = sp.run(
        dotfiles._git_base + ["show", f"{commit_hash}:{target}"],
        capture_output=True, text=True,
    ).stdout

    fzf_calls = [[target], [commit_line]]
    with patch("pydymenu.fzf", side_effect=fzf_calls):
        History(dotfiles, editor=mock_editor).run()

    temp_file = mock_editor.open.call_args[0][0][1]
    assert temp_file.read_text() == expected


# -- ChangeDir tests --


def test_cd_exits_on_no_selection(clean_repo):
    """ChangeDir should sys.exit when fzf returns None."""
    dotfiles = clean_repo["df"]
    with patch("pydymenu.fzf", return_value=None):
        with pytest.raises(SystemExit):
            ChangeDir(dotfiles).run()


def test_cd_runs_default_listing(clean_repo, monkeypatch):
    """ChangeDir should run 'ls -lA --color=auto' when MYDOT_CD_CMD is unset."""
    dotfiles = clean_repo["df"]
    worktree = clean_repo["worktree"]
    monkeypatch.delenv("MYDOT_CD_CMD", raising=False)
    monkeypatch.setenv("SHELL", "/bin/sh")
    # warm cached properties so subprocess.run patch only sees our calls
    _ = dotfiles.list_all

    expected_dir = (worktree / "fileA").resolve().parent

    with patch("pydymenu.fzf", return_value=["fileA"]), \
         patch("mydot.actions.subprocess.run") as mock_run:
        ChangeDir(dotfiles).run()

    listing_call = mock_run.call_args_list[0]
    assert listing_call == call(
        ["ls", "-lA", "--color=auto"], cwd=expected_dir
    )


def test_cd_runs_custom_listing(clean_repo, monkeypatch):
    """ChangeDir should use MYDOT_CD_CMD when set."""
    dotfiles = clean_repo["df"]
    worktree = clean_repo["worktree"]
    monkeypatch.setenv("MYDOT_CD_CMD", "eza -la")
    monkeypatch.setenv("SHELL", "/bin/sh")
    _ = dotfiles.list_all

    expected_dir = (worktree / "fileA").resolve().parent

    with patch("pydymenu.fzf", return_value=["fileA"]), \
         patch("mydot.actions.subprocess.run") as mock_run:
        ChangeDir(dotfiles).run()

    listing_call = mock_run.call_args_list[0]
    assert listing_call == call(["eza", "-la"], cwd=expected_dir)


def test_cd_spawns_shell(clean_repo, monkeypatch):
    """ChangeDir should spawn $SHELL with cwd set to the target directory."""
    dotfiles = clean_repo["df"]
    worktree = clean_repo["worktree"]
    monkeypatch.setenv("SHELL", "/bin/zsh")
    monkeypatch.delenv("MYDOT_CD_CMD", raising=False)
    _ = dotfiles.list_all

    expected_dir = (worktree / "fileA").resolve().parent

    with patch("pydymenu.fzf", return_value=["fileA"]), \
         patch("mydot.actions.subprocess.run") as mock_run:
        ChangeDir(dotfiles).run()

    shell_call = mock_run.call_args_list[1]
    assert shell_call == call(["/bin/zsh"], cwd=expected_dir)


def test_cd_returns_target_dir(clean_repo, monkeypatch):
    """ChangeDir.run() should return the resolved parent directory."""
    dotfiles = clean_repo["df"]
    worktree = clean_repo["worktree"]
    monkeypatch.setenv("SHELL", "/bin/sh")
    monkeypatch.delenv("MYDOT_CD_CMD", raising=False)
    _ = dotfiles.list_all

    expected_dir = (worktree / "fileA").resolve().parent

    with patch("pydymenu.fzf", return_value=["fileA"]), \
         patch("mydot.actions.subprocess.run"):
        result = ChangeDir(dotfiles).run()

    assert result == expected_dir
