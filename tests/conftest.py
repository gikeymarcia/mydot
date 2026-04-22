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


@pytest.fixture
def submodule_repo(tmp_path):
    """A bare repo with a submodule and a nested submodule (depth=2)."""
    import os

    bare = tmp_path / "bare"
    worktree = tmp_path / "worktree"
    bare.mkdir()
    worktree.mkdir()
    sp.run(["git", "init", "--bare", bare], capture_output=True)

    def parent_git(*args):
        cmd = ["git", f"--git-dir={bare}", f"--work-tree={worktree}"]
        return sp.run(cmd + list(args), capture_output=True, text=True)

    # Allow local file:// transport for submodule cloning
    parent_git("config", "protocol.file.allow", "always")

    # Create a regular file in parent repo
    top_file = worktree / "topfile"
    top_file.write_text("top level file\n")
    parent_git("add", str(top_file))
    parent_git("commit", "-m", "add topfile")

    # -- Create the inner submodule origin (depth=2) --
    inner_origin = tmp_path / "inner_origin"
    inner_origin.mkdir()
    sp.run(["git", "init", inner_origin], capture_output=True)
    (inner_origin / "inner.conf").write_text("inner config\n")
    sp.run(["git", "add", "inner.conf"], capture_output=True, cwd=inner_origin)
    sp.run(["git", "commit", "-m", "inner init"], capture_output=True, cwd=inner_origin)

    # -- Create the outer submodule origin --
    outer_origin = tmp_path / "outer_origin"
    outer_origin.mkdir()
    sp.run(["git", "init", outer_origin], capture_output=True)
    (outer_origin / "tmux.conf").write_text("set -g mouse on\n")
    sp.run(["git", "add", "tmux.conf"], capture_output=True, cwd=outer_origin)
    sp.run(["git", "commit", "-m", "outer init"], capture_output=True, cwd=outer_origin)
    # Add inner as nested submodule of outer
    sp.run(
        ["git", "-c", "protocol.file.allow=always",
         "submodule", "add", str(inner_origin), "plugins/inner"],
        capture_output=True, cwd=outer_origin,
    )
    sp.run(["git", "commit", "-m", "add inner submodule"],
           capture_output=True, cwd=outer_origin)

    # -- Add outer submodule to parent bare repo --
    env = os.environ.copy()
    env["GIT_DIR"] = str(bare)
    env["GIT_WORK_TREE"] = str(worktree)
    sp.run(
        ["git", "-c", "protocol.file.allow=always",
         "submodule", "add", str(outer_origin), "config/tmux"],
        capture_output=True, cwd=worktree, env=env,
    )
    parent_git("add", "-A")
    parent_git("commit", "-m", "add outer submodule")

    # Initialize nested submodules recursively (depth=2)
    sp.run(
        ["git", "-c", "protocol.file.allow=always",
         "submodule", "update", "--init", "--recursive"],
        capture_output=True, cwd=worktree, env=env,
    )

    return {
        "bare": bare,
        "worktree": worktree,
        "git": parent_git,
        "df": mydot.Repository(bare, worktree),
    }


@pytest.fixture
def submodule_with_staged_inner_file(submodule_repo):
    """A submodule_repo where a new file has been `git add`-ed inside the
    submodule but not yet committed by the inner git.

    Models the real-world workflow:
      1. cd into submodule
      2. create a file
      3. git add it (inside the submodule)
      4. return to parent — the file should still show up in d. edit
    """
    worktree = submodule_repo["worktree"]
    sub_dir = worktree / "config" / "tmux"
    new_file = sub_dir / "new-staged.conf"
    new_file.write_text("set -g prefix C-a\n")
    # Stage it inside the submodule — NO commit.
    sp.run(["git", "add", "new-staged.conf"], capture_output=True, cwd=sub_dir, check=True)
    submodule_repo["df"].freshen()
    return submodule_repo


@pytest.fixture
def staged_submodule_repo(tmp_path):
    """A bare repo with a submodule staged but NOT committed."""
    import os

    bare = tmp_path / "bare"
    worktree = tmp_path / "worktree"
    bare.mkdir()
    worktree.mkdir()
    sp.run(["git", "init", "--bare", bare], capture_output=True)

    def parent_git(*args):
        cmd = ["git", f"--git-dir={bare}", f"--work-tree={worktree}"]
        return sp.run(cmd + list(args), capture_output=True, text=True)

    parent_git("config", "protocol.file.allow", "always")

    # Create a regular file and commit it (so HEAD exists)
    top_file = worktree / "topfile"
    top_file.write_text("top level file\n")
    parent_git("add", str(top_file))
    parent_git("commit", "-m", "add topfile")

    # Create an outer submodule origin
    outer_origin = tmp_path / "outer_origin"
    outer_origin.mkdir()
    sp.run(["git", "init", outer_origin], capture_output=True)
    (outer_origin / "tmux.conf").write_text("set -g mouse on\n")
    sp.run(["git", "add", "tmux.conf"], capture_output=True, cwd=outer_origin)
    sp.run(["git", "commit", "-m", "outer init"], capture_output=True, cwd=outer_origin)

    # Add outer submodule to parent — stage but do NOT commit
    env = os.environ.copy()
    env["GIT_DIR"] = str(bare)
    env["GIT_WORK_TREE"] = str(worktree)
    sp.run(
        ["git", "-c", "protocol.file.allow=always",
         "submodule", "add", str(outer_origin), "config/tmux"],
        capture_output=True, cwd=worktree, env=env,
    )
    parent_git("add", "-A")
    # Deliberately NO commit here — submodule is staged only

    return {
        "bare": bare,
        "worktree": worktree,
        "git": parent_git,
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
