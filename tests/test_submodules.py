from pathlib import Path

import pytest


def test_submodule_entries_detected(submodule_repo):
    dotfiles = submodule_repo["df"]
    entries = dotfiles._submodule_entries()
    assert "config/tmux" in entries


def test_tracked_excludes_submodule_dirs(submodule_repo):
    """Submodule directory entries (mode 160000) should not appear in tracked."""
    dotfiles = submodule_repo["df"]
    tracked = dotfiles.tracked
    assert "config/tmux" not in tracked
    assert "topfile" in tracked


def test_submodule_files_listed(submodule_repo):
    """submodule_files should return files inside the submodule with prefixed paths."""
    dotfiles = submodule_repo["df"]
    sub_files = dotfiles.submodule_files
    assert "config/tmux/tmux.conf" in sub_files


def test_list_all_includes_submodule_files(submodule_repo):
    dotfiles = submodule_repo["df"]
    all_files = dotfiles.list_all
    assert "topfile" in all_files
    assert "config/tmux/tmux.conf" in all_files


def test_nested_submodule_depth_2(submodule_repo):
    """Files from a submodule-of-submodule should appear (depth=2)."""
    dotfiles = submodule_repo["df"]
    sub_files = dotfiles.submodule_files
    assert "config/tmux/plugins/inner/inner.conf" in sub_files


def test_list_all_includes_nested_submodule(submodule_repo):
    dotfiles = submodule_repo["df"]
    all_files = dotfiles.list_all
    assert "config/tmux/plugins/inner/inner.conf" in all_files


def test_depth_limit_respected(submodule_repo):
    """_list_submodule_files with depth=0 returns nothing."""
    dotfiles = submodule_repo["df"]
    result = dotfiles._list_submodule_files("config/tmux", depth=0)
    assert result == []


def test_depth_1_excludes_nested(submodule_repo):
    """depth=1 should get outer submodule files but not nested submodule files."""
    dotfiles = submodule_repo["df"]
    result = dotfiles._list_submodule_files("config/tmux", depth=1)
    assert "config/tmux/tmux.conf" in result
    nested = [f for f in result if "inner" in f]
    assert nested == []


def test_no_submodules_unchanged(clean_repo):
    """A repo without submodules should have empty submodule_files."""
    dotfiles = clean_repo["df"]
    assert dotfiles.submodule_files == []
    assert dotfiles._submodule_entries() == []
    assert dotfiles.list_all == sorted(dotfiles.tracked)


def test_missing_submodule_dir_graceful(submodule_repo):
    """If a submodule directory doesn't exist on disk, return [] without crashing."""
    dotfiles = submodule_repo["df"]
    result = dotfiles._list_submodule_files("nonexistent/path", depth=2)
    assert result == []


def test_freshen_clears_submodule_files(submodule_repo):
    dotfiles = submodule_repo["df"]
    _ = dotfiles.submodule_files
    assert "submodule_files" in dotfiles.__dict__

    dotfiles.freshen()
    assert "submodule_files" not in dotfiles.__dict__


def test_resolve_git_dir_directory(submodule_repo):
    """_resolve_submodule_git_dir handles .git as a directory."""
    dotfiles = submodule_repo["df"]
    worktree = submodule_repo["worktree"]
    # Create a fake submodule with .git as a directory inside the worktree
    fake_sub = worktree / "fakesub"
    fake_sub.mkdir()
    dot_git = fake_sub / ".git"
    dot_git.mkdir()
    result = dotfiles._resolve_submodule_git_dir("fakesub")
    assert result == dot_git


def test_resolve_git_dir_file_pointer(submodule_repo):
    """_resolve_submodule_git_dir handles .git file with gitdir: pointer."""
    dotfiles = submodule_repo["df"]
    # The real submodule should have a .git file with gitdir: pointer
    result = dotfiles._resolve_submodule_git_dir("config/tmux")
    assert result is not None
    assert result.is_dir()


# -- Staged (uncommitted) submodule tests --


def test_staged_submodule_entries_detected(staged_submodule_repo):
    """_submodule_entries() should find submodules that are staged but not committed."""
    dotfiles = staged_submodule_repo["df"]
    entries = dotfiles._submodule_entries()
    assert "config/tmux" in entries


def test_staged_submodule_files_listed(staged_submodule_repo):
    """submodule_files should include files from a staged-but-uncommitted submodule."""
    dotfiles = staged_submodule_repo["df"]
    sub_files = dotfiles.submodule_files
    assert "config/tmux/tmux.conf" in sub_files


def test_staged_list_all_includes_submodule_files(staged_submodule_repo):
    """list_all should include both regular tracked files and staged submodule files."""
    dotfiles = staged_submodule_repo["df"]
    all_files = dotfiles.list_all
    assert "topfile" in all_files
    assert "config/tmux/tmux.conf" in all_files


# -- File staged (uncommitted) INSIDE a submodule --


def test_staged_file_inside_submodule_listed(submodule_with_staged_inner_file):
    """A file staged (but not committed) inside a submodule should appear."""
    dotfiles = submodule_with_staged_inner_file["df"]
    assert "config/tmux/new-staged.conf" in dotfiles.submodule_files
    assert "config/tmux/new-staged.conf" in dotfiles.list_all
    # Sanity: committed file in the submodule is still listed.
    assert "config/tmux/tmux.conf" in dotfiles.submodule_files
