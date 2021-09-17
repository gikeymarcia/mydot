# standard library
from pathlib import Path
import subprocess as sp
from typing import List

import pytest

import mydot


@pytest.fixture
def fake_repo(tmp_path):
    class GitContoller:
        def __init__(self, git_dir: Path, worktree: Path):
            self.git_dir = git_dir
            self.worktree = worktree

        def __call__(self, args: list) -> sp.CompletedProcess:
            cmd = ["git", f"--git-dir={self.git_dir}", f"--work-tree={self.worktree}"]
            return sp.run(cmd + args, capture_output=True, text=True)

    # make worktree, init --bare repo, instantiate a GitContoller
    bare = tmp_path / "bare"
    worktree = tmp_path / "worktree"
    [d.mkdir() for d in [bare, worktree]]
    init = ["git", "init", "--bare", bare]
    sp.run(init, capture_output=True)
    git_action = GitContoller(bare, worktree)

    # populate worktree stages: first > edit > delete > stage > create
    repofiles = [
        {
            "path": worktree / "unmodified",
            "stages": ["first"],
            "appears in": ["list", "tracked"],
        },
        {
            "path": worktree / "space folder/unmodified",
            "stages": ["first"],
            "appears in": ["list", "tracked"],
        },
        {
            "path": worktree / "modified staged changes",
            "stages": ["first"],
            "appears in": ["staged", "list", "restore", "tracked"],
        },
        {
            "path": worktree / "modified unstaged changes",
            "stages": ["first", "edit"],
            "appears in": ["add", "list", "restore", "modified_unstaged", "tracked"],
        },
        {
            "path": worktree / "deleted staged",
            "stages": ["first", "delete", "stage"],
            "appears in": ["deleted", "staged", "restore", "tracked"],
        },
        {
            "path": worktree / "in folder/modified staged",
            "stages": ["first", "edit", "stage"],
            "appears in": ["staged", "list", "restore", "modified_staged", "tracked"],
        },
        {
            "path": worktree / "in folder/modified unstaged",
            "stages": ["first", "edit"],
            "appears in": ["add", "list", "restore", "modified_unstaged", "tracked"],
        },
        {
            "path": worktree / "deleted unstaged",
            "stages": ["first", "delete"],
            "appears in": ["add", "list", "restore", "modified_unstaged", "tracked"],
        },
        {
            "path": worktree / "oldname",
            "stages": ["first"],
            "appears in": ["staged", "oldname", "tracked"],
        },
        {
            "path": worktree / "rename",
            "stages": ["rename"],
            "appears in": ["list", "staged"],
            "from": worktree / "oldname",
        },
        {
            "path": worktree / "newfile",
            "stages": ["create"],
            "appears in": [],
        },
        {
            "path": worktree / "add me-fool",
            "stages": ["create", "add"],
            "appears in": ["adds_staged"],
        },
    ]

    # first: make files and commit
    for file in repofiles:
        fp, stages = file["path"], file["stages"]
        if "first" in stages:
            if not fp.parent.is_dir():
                fp.parent.mkdir(parents=True)
            fp.touch()
            fp.write_text(f"data for {fp}")
            git_action(["add", fp])
    git_action(["commit", "-m", "first commit"])

    # edit / delete / stage / create
    for file in repofiles:
        fp, stages = file["path"], file["stages"]
        if "edit" in stages:
            fp.write_text(f"edited content for {fp}")
        if "delete" in stages:
            fp.unlink()
        if "rename" in stages:
            oldname = file["from"]
            git_action(["mv", oldname, fp])
        if "stage" in stages:
            git_action(["add", fp])
        if "create" in stages:
            fp.touch()
            fp.write_text(f"new file {fp}")
        if "add" in stages:
            git_action(["add", fp])

    return {
        "bare": bare,
        "worktree": worktree,
        "init": init,
        "git": git_action,
        "repofiles": repofiles,
        "df": mydot.Dotfiles(bare, worktree),
        "status": git_action(["status"]).stdout,
        "tree": sp.run(["tree", "-C", "-p", worktree], capture_output=True),
    }


def appears_in(fake: dict, key: str) -> List[str]:
    """Filters a fake_repo return list where the 'key' in 'appears_in'."""
    filtered = [
        str(file["path"].relative_to(fake["worktree"]))
        for file in fake["repofiles"]
        if key in file["appears in"]
    ]
    return sorted(filtered)


def test_tracked(fake_repo):
    dotfiles = fake_repo["df"]
    tracked = appears_in(fake_repo, "tracked")
    assert dotfiles.tracked == tracked


# def test_list_all(fake_repo):
#     dotfiles = fake_repo["df"]
#     list_all = appears_in(fake_repo, "list")
#     [print(line) for line in fake_repo["status"].split("\n")]
#     assert dotfiles.list_all == list_all


def test_oldnames(fake_repo):
    dotfiles = fake_repo["df"]
    old = appears_in(fake_repo, "oldname")
    assert dotfiles.oldnames == old


def test_adds_staged(fake_repo):
    dotfiles = fake_repo["df"]
    adds = appears_in(fake_repo, "adds_staged")
    assert dotfiles.adds_staged == adds
    for file in adds:
        fake_repo["git"](["restore", "--staged", file])
    dotfiles.freshen()
    assert dotfiles.adds_staged == []


def test_deleted_staged(fake_repo):
    dotfiles = fake_repo["df"]
    deleted = appears_in(fake_repo, "deleted")
    assert dotfiles.deleted_staged == deleted
    for file in deleted:
        fake_repo["git"](["restore", "--staged", "--", file])
    dotfiles.freshen()
    assert dotfiles.deleted_staged == []


def test_modfied_staged(fake_repo):
    dotfiles = fake_repo["df"]
    modified_staged = appears_in(fake_repo, "modified_staged")
    assert dotfiles.modified_staged == modified_staged
    for file in modified_staged:
        fake_repo["git"](["restore", "--staged", "--", file])
    dotfiles.freshen()
    assert dotfiles.modified_staged == []


def test_modfied_UNstaged(fake_repo):
    dotfiles = fake_repo["df"]
    modified_unstaged = appears_in(fake_repo, "modified_unstaged")
    assert dotfiles.modified_unstaged == modified_unstaged
    for file in modified_unstaged:
        fake_repo["git"](["add", "--", file])
    dotfiles.freshen()
    assert dotfiles.modified_unstaged == []


# TODO:
# - files renamed
# - Modified / Added / Rename
# subcommand ADD:
#   test: "adding" deleted files
#   test: only listing files with unstaged changes (git ls-files?)
#   test: make sure things don't break with a clean worktree
# example: -ls didn't work until I modified staged_adds()

# vim: foldlevel=1:
