#!/usr/bin/env python3
# Mikey Garcia, @gikeymarcia
# https://github.com/gikeymarcia/mydot

# standard library
from pathlib import Path
import subprocess as sp
from typing import List, Union

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

    # populate worktree stages: first > edit > delete > stage > create > edit2
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
            "stages": ["first", "edit", "stage"],
            "appears in": ["list", "restore", "tracked", "modified_staged"],
        },
        {
            "path": worktree / "modified partial staged",
            "stages": ["first", "edit", "stage", "edit2"],
            "appears in": [
                "add",
                "list",
                "discard",
                "modified_unstaged",
                "modified_staged",
                "tracked",
                "restore",
            ],
        },
        {
            "path": worktree / "modified unstaged changes",
            "stages": ["first", "edit"],
            "appears in": ["add", "list", "discard", "modified_unstaged", "tracked"],
        },
        {
            "path": worktree / "deleted staged",
            "stages": ["first", "delete", "stage"],
            "appears in": ["deleted", "restore", "tracked"],
        },
        {
            "path": worktree / "in folder/modified staged",
            "stages": ["first", "edit", "stage"],
            "appears in": ["list", "restore", "modified_staged", "tracked"],
        },
        {
            "path": worktree / "in folder/modified unstaged",
            "stages": ["first", "edit"],
            "appears in": ["add", "list", "discard", "modified_unstaged", "tracked"],
        },
        {
            "path": worktree / "deleted unstaged",
            "stages": ["first", "delete"],
            "appears in": ["add", "list", "discard", "modified_unstaged", "tracked"],
        },
        # renames
        {
            "path": worktree / "oldname-edits",
            "stages": ["first", "edit"],
            "appears in": ["oldname", "tracked"],
        },
        {
            "path": worktree / "rename-edits",
            "stages": ["rename"],
            "appears in": ["list", "modified_unstaged", "rename"],
            "from": worktree / "oldname-edits",
        },
        {
            "path": worktree / "oldname",
            "stages": ["first"],
            "appears in": ["oldname", "tracked"],
        },
        {
            "path": worktree / "rename",
            "stages": ["rename"],
            "appears in": ["list", "rename"],
            "from": worktree / "oldname",
        },
        # new files
        {
            "path": worktree / "newfile",
            "stages": ["create"],
            "appears in": [],
        },
        {
            "path": worktree / "newly added",
            "stages": ["create", "add"],
            "appears in": ["adds_staged", "list", "restore"],
        },
        {
            "path": worktree / "added then modified",
            "stages": ["create", "add", "edit2"],
            "appears in": ["adds_staged", "list", "restore", "modified_unstaged"],
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

    # edit / delete / rename / stage / create / add / edit2
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
        if "edit2" in stages:
            fp.write_text(f"re-edited content for {fp}")

    def run_status():
        for line in git_action(["status", "-s", "--porcelain"]).stdout.split("\n"):
            print(line)

    return {
        "bare": bare,
        "worktree": worktree,
        "init": init,
        "git": git_action,
        "repofiles": repofiles,
        "df": mydot.Repository(bare, worktree),
        "status": run_status,
        "tree": sp.run(["tree", "-C", "-p", worktree], capture_output=True),
    }


def appears_in(fake: dict, keys: Union[List[str], str]) -> List[str]:
    """Filters a fake repo return object by given keys.

    You can pass in a single key as a str or List[str] of keys.
    Only files matching all given keys are returned.
    Matches are those files with the keys in their 'appears in' list
    """
    filters = [keys] if isinstance(keys, str) else keys
    matches = []
    for file in fake["repofiles"]:
        for key in filters:
            if key not in file["appears in"]:
                break
        else:
            matches.append(str(file["path"].relative_to(fake["worktree"])))
    return sorted(matches)


def test_tracked(fake_repo):
    dotfiles = fake_repo["df"]
    tracked = appears_in(fake_repo, "tracked")
    assert dotfiles.tracked == tracked


def test_list_all(fake_repo):
    dotfiles = fake_repo["df"]
    fake_repo["status"]()
    list_all = appears_in(fake_repo, "list")
    assert dotfiles.list_all == list_all


def test_oldnames(fake_repo):
    dotfiles = fake_repo["df"]
    dotfiles.freshen()
    fake_repo["status"]()
    old = appears_in(fake_repo, "oldname")
    assert dotfiles.oldnames == old


def test_renames(fake_repo):
    dotfiles = fake_repo["df"]
    dotfiles.freshen()
    fake_repo["status"]()
    renames = appears_in(fake_repo, "rename")
    assert dotfiles.renames == renames


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
    fake_repo["status"]()
    modified_unstaged = appears_in(fake_repo, "modified_unstaged")
    assert dotfiles.modified_unstaged == sorted(modified_unstaged)
    for file in modified_unstaged:
        fake_repo["git"](["add", "--", file])
    dotfiles.freshen()
    assert dotfiles.modified_unstaged == []


def test_restorables(fake_repo):
    dotfiles = fake_repo["df"]
    fake_repo["status"]()
    restorable = appears_in(fake_repo, "restore")
    assert dotfiles.restorables == restorable


# TODO:
# - Modified / Added / Rename
# subcommand ADD:
#   test: "adding" deleted files
#   test: make sure things don't break with a clean worktree

# vim: foldlevel=1:
