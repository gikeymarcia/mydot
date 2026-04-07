import subprocess as sp
from pathlib import Path
from typing import List, Union

import pytest

import mydot


@pytest.fixture
def fake_repo(tmp_path):
    class GitController:
        def __init__(self, git_dir: Path, worktree: Path):
            self.git_dir = git_dir
            self.worktree = worktree

        def __call__(self, args: list) -> sp.CompletedProcess:
            cmd = ["git", f"--git-dir={self.git_dir}", f"--work-tree={self.worktree}"]
            return sp.run(cmd + args, capture_output=True, text=True)

    bare = tmp_path / "bare"
    worktree = tmp_path / "worktree"
    [d.mkdir() for d in [bare, worktree]]
    sp.run(["git", "init", "--bare", bare], capture_output=True)
    git_action = GitController(bare, worktree)

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

    for file in repofiles:
        fp, stages = file["path"], file["stages"]
        if "first" in stages:
            if not fp.parent.is_dir():
                fp.parent.mkdir(parents=True)
            fp.touch()
            fp.write_text(f"data for {fp}")
            git_action(["add", fp])
    git_action(["commit", "-m", "first commit"])

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
        "git": git_action,
        "repofiles": repofiles,
        "df": mydot.Repository(bare, worktree),
        "status": run_status,
    }


@pytest.fixture
def clean_repo(tmp_path):
    """A repo with committed files and no pending changes."""
    bare = tmp_path / "bare"
    worktree = tmp_path / "worktree"
    bare.mkdir()
    worktree.mkdir()
    sp.run(["git", "init", "--bare", bare], capture_output=True)

    def git(*args):
        cmd = ["git", f"--git-dir={bare}", f"--work-tree={worktree}"]
        return sp.run(cmd + list(args), capture_output=True, text=True)

    for name in ["fileA", "fileB", "fileC"]:
        f = worktree / name
        f.write_text(f"content of {name}\n")
        git("add", str(f))
    git("commit", "-m", "initial commit")

    return {
        "bare": bare,
        "worktree": worktree,
        "git": git,
        "df": mydot.Repository(bare, worktree),
    }


def appears_in(fake: dict, keys: Union[List[str], str]) -> List[str]:
    """Filters a fake repo return object by given keys."""
    filters = [keys] if isinstance(keys, str) else keys
    matches = []
    for file in fake["repofiles"]:
        for key in filters:
            if key not in file["appears in"]:
                break
        else:
            matches.append(str(file["path"].relative_to(fake["worktree"])))
    return sorted(matches)
