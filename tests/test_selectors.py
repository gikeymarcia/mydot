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
            "appears in": ["list"],
        },
        {
            "path": worktree / "space folder/unmodified",
            "stages": ["first"],
            "appears in": ["list"],
        },
        {
            "path": worktree / "modified staged changes",
            "stages": ["first"],
            "appears in": ["staged", "list", "restore"],
        },
        {
            "path": worktree / "modified unstaged changes",
            "stages": ["first", "edit"],
            "appears in": ["add", "list", "restore", "modified_unstaged"],
        },
        {
            "path": worktree / "deleted staged",
            "stages": ["first", "delete", "stage"],
            "appears in": ["deleted", "staged", "restore"],
        },
        {
            "path": worktree / "in folder/modified staged",
            "stages": ["first", "edit", "stage"],
            "appears in": ["staged", "list", "restore", "modified_staged"],
        },
        {
            "path": worktree / "in folder/modified unstaged",
            "stages": ["first", "edit"],
            "appears in": ["add", "list", "restore", "modified_unstaged"],
        },
        {
            "path": worktree / "deleted unstaged",
            "stages": ["first", "delete"],
            "appears in": ["add", "list", "restore", "modified_unstaged"],
        },
        {
            "path": worktree / "oldname",
            "stages": ["first"],
            "appears in": ["staged"],
        },
        {
            "path": worktree / "newfile",
            "stages": ["create"],
            "appears in": [],
        },
        {
            "path": worktree / "rename",
            "stages": ["rename"],
            "appears in": ["list", "staged"],
            "from": worktree / "oldname",
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


def test_deleted_staged(fake_repo):
    dotfiles = fake_repo["df"]
    deleted = appears_in(fake_repo, "deleted")
    assert dotfiles.deleted_staged == deleted
    for file in deleted:
        fake_repo["git"](["restore", "--staged", "--", file])
    new_df = mydot.Dotfiles(fake_repo["bare"], fake_repo["worktree"])
    assert new_df.deleted_staged == []


def test_modfied_staged(fake_repo):
    dotfiles = fake_repo["df"]
    modified_staged = appears_in(fake_repo, "modified_staged")
    assert dotfiles.modified_staged == modified_staged
    for file in modified_staged:
        fake_repo["git"](["restore", "--staged", "--", file])
    new_df = mydot.Dotfiles(fake_repo["bare"], fake_repo["worktree"])
    assert new_df.modified_staged == []


def test_modfied_UNstaged(fake_repo):
    dotfiles = fake_repo["df"]
    modified_unstaged = appears_in(fake_repo, "modified_unstaged")
    assert dotfiles.modified_unstaged == modified_unstaged
    for file in modified_unstaged:
        fake_repo["git"](["add", "--", file])
    new_df = mydot.Dotfiles(fake_repo["bare"], fake_repo["worktree"])
    assert new_df.modified_unstaged == []


# def test_list_all(fake_repo):
#     worktree, repofiles = fake_repo["worktree"], fake_repo["repofiles"]
#     dotfiles = fake_repo["df"]
#     list_files = sorted(
#         [
#             str(f["path"].relative_to(worktree))
#             for f in repofiles
#             if "list" in f["appears in"]
#         ]
#     )
#     print(f"{list_files= }")
#     print(dotfiles.short_status)
#     print(fake_repo["status"])
#     for f in list_files:
#         if f not in dotfiles.list_all:
#             print(f"missing from df: {f}")
#     for f in dotfiles.list_all:
#         if f not in list_files:
#             print(f"shouldn't be in list_files: {f}")
#     assert list_files == dotfiles.list_all


# TODO:
# - files renamed
# - Modified / Added / Rename
# subcommand ADD:
#   test: "adding" deleted files
#   test: only listing files with unstaged changes (git ls-files?)
#   test: make sure things don't break with a clean worktree
# example: -ls didn't work until I modified staged_adds()

# vim: foldlevel=1:
