"""Tests for Repository helpers added for the `watch` TUI."""
import subprocess as sp
from pathlib import Path


def test_branch_name(clean_repo):
    df = clean_repo["df"]
    name = df.branch_name()
    assert name  # non-empty: whatever init.defaultBranch is configured


def test_remote_url_empty_when_unset(clean_repo):
    df = clean_repo["df"]
    assert df.remote_url() == ""


def test_remote_url_returns_origin(clean_repo):
    df = clean_repo["df"]
    clean_repo["git"]("remote", "add", "origin", "git@example.com:me/repo.git")
    assert df.remote_url() == "git@example.com:me/repo.git"


def test_unstaged_modified_files(clean_repo):
    df = clean_repo["df"]
    f = clean_repo["worktree"] / "fileA"
    f.write_text("changed\n")
    df.freshen()
    assert "fileA" in df.modified_unstaged


def test_diff_for_unstaged_file(clean_repo):
    df = clean_repo["df"]
    f = clean_repo["worktree"] / "fileA"
    f.write_text("changed\n")
    df.freshen()
    diff = df.diff_for("fileA", staged=False, color=False)
    assert "fileA" in diff
    assert "+changed" in diff


def test_diff_for_staged_file(clean_repo):
    df = clean_repo["df"]
    f = clean_repo["worktree"] / "fileA"
    f.write_text("staged-change\n")
    clean_repo["git"]("add", str(f))
    df.freshen()
    diff = df.diff_for("fileA", staged=True, color=False)
    assert "+staged-change" in diff


def test_stage_file(clean_repo):
    df = clean_repo["df"]
    f = clean_repo["worktree"] / "fileA"
    f.write_text("toedit\n")
    df.freshen()
    df.stage("fileA")
    df.freshen()
    assert "fileA" in df.modified_staged


def test_unstage_file(clean_repo):
    df = clean_repo["df"]
    f = clean_repo["worktree"] / "fileA"
    f.write_text("toedit\n")
    clean_repo["git"]("add", str(f))
    df.freshen()
    assert "fileA" in df.modified_staged
    df.unstage("fileA")
    df.freshen()
    assert "fileA" not in df.modified_staged
    assert "fileA" in df.modified_unstaged


