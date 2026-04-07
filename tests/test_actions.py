import os
import subprocess as sp
import tarfile
from pathlib import Path
from unittest.mock import patch, MagicMock

import pytest

import mydot
from mydot.actions import (
    AddChanges,
    DiscardChanges,
    GitPassthrough,
    Grep,
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
