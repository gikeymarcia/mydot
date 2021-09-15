# standard library
from pathlib import Path
import subprocess as sp

import pytest

import mydot
from mydot.exceptions import MissingRepositoryLocation


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


@pytest.fixture
def defined_dot():
    dots = Path.home() / ".config/dotfiles"
    work = Path.home()
    return mydot.Dotfiles(git_dir=dots, work_tree=work)


def test_import_module():
    assert mydot


def test_defined_repo_and_work_tree(defined_dot):
    assert defined_dot.bare_repo == Path.home() / ".config/dotfiles"
    assert defined_dot.work_tree == Path.home()


def test_env_defined_repo_with_default_work_tree(monkeypatch, tmpdir):
    monkeypatch.setenv("DOTFILES", str(tmpdir))
    default_vals = mydot.Dotfiles()
    assert default_vals.bare_repo == Path(str(tmpdir))
    assert default_vals.work_tree == Path.home()


def test_missing_DOTFILES_in_env(monkeypatch):
    monkeypatch.delenv("DOTFILES", raising=False)
    with pytest.raises(MissingRepositoryLocation) as except_info:
        _ = mydot.Dotfiles()
    assert except_info.type is MissingRepositoryLocation


def test_fake_repo_deleted_staged(fake_repo):
    dotfiles = fake_repo["df"]
    deleted = sorted(
        [
            str(f["path"].relative_to(fake_repo["worktree"]))
            for f in fake_repo["repofiles"]
            if "deleted" in f["appears in"]
        ]
    )
    assert dotfiles.deleted_staged == deleted
    for file in deleted:
        fake_repo["git"](["restore", "--staged", "--", file])
    assert dotfiles.deleted_staged == []


def test_fake_repo_modfied_staged(fake_repo):
    dotfiles = fake_repo["df"]
    modified_staged = sorted(
        [
            str(f["path"].relative_to(fake_repo["worktree"]))
            for f in fake_repo["repofiles"]
            if "modified_staged" in f["appears in"]
        ]
    )
    assert dotfiles.modified_staged == modified_staged
    for file in modified_staged:
        fake_repo["git"](["restore", "--staged", "--", file])
    assert dotfiles.modified_staged == []


def test_fake_repo_modfied_UNstaged(fake_repo):
    dotfiles = fake_repo["df"]
    modified_unstaged = sorted(
        [
            str(f["path"].relative_to(fake_repo["worktree"]))
            for f in fake_repo["repofiles"]
            if "modified_unstaged" in f["appears in"]
        ]
    )
    assert dotfiles.modified_unstaged == modified_unstaged
    for file in modified_unstaged:
        fake_repo["git"](["add", "--", file])
    assert dotfiles.modified_unstaged == []


# def test_fake_repo_list_all(fake_repo):
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
