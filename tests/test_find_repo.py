# standard library
from pathlib import Path
import subprocess as sp

# my project
import mydot
from mydot.exceptions import MissingRepositoryLocation

# from pypi
import pytest


@pytest.fixture
def fake_repo_and_work_tree(tmp_path):
    def super_touch(path_obj: Path):
        if not path_obj.parent.exists():
            path_obj.parent.mkdir(parents=True)
        path_obj.touch()
        path_obj.write_text("first commit")

    def git_do(arg_list, git_dir, work_tree):
        base = ["git", f"--git-dir={git_dir}", f"--work-tree={work_tree}"]
        sp.run(base + arg_list)

    # make and init --bare repo
    bare = tmp_path / "bare"
    bare.mkdir()
    create_cmd = ["git", "init", "--bare", bare]
    sp.run(create_cmd)

    # make and populate work tree
    work = tmp_path / "work"
    work.mkdir()
    files = [
        Path.joinpath(work, f)
        for f in ["README", "project/__init__.py", "LICENSE", "CHANGELOG"]
    ]
    [super_touch(f) for f in files]
    git_do(["add", "-v", "--", files[0]], bare, work)
    git_do(["add", "-v", "--", files[2]], bare, work)
    git_do(["commit", "-m", "first!"], bare, work)
    files[0].write_text("more stuff")
    git_do(["add", "-v", "--", files[1]], bare, work)
    git_do(["config", "--local", "status.showUntrackedFiles", "no"], bare, work)
    git_do(["status", "-s"], bare, work)
    sp.run(["tree", work])
    return {"bare": bare, "worktree": work, "create": create_cmd, "do": git_do}


@pytest.fixture
def defined_dot():
    return mydot.Dotfiles(
        git_dir="/home/mikey/.config/dotfiles", work_tree="/home/mikey"
    )


def test_import_module():
    assert mydot


def test_constructor():
    assert mydot.Dotfiles(
        git_dir="/home/mikey/.config/dotfiles", work_tree="/home/mikey"
    )


def test_defined_repo_and_work_tree(defined_dot):
    assert defined_dot.bare_repo == Path("/home/mikey/.config/dotfiles")
    assert defined_dot.work_tree == Path("/home/mikey/")


def test_default_repo_and_work_tree(monkeypatch, tmpdir):
    monkeypatch.setenv("DOTFILES", str(tmpdir))
    default_vals = mydot.Dotfiles()
    assert default_vals.bare_repo == Path(str(tmpdir))
    assert default_vals.work_tree == Path.home()


def test_missing_DOTFILES_in_env(monkeypatch):
    monkeypatch.delenv("DOTFILES", raising=False)
    with pytest.raises(MissingRepositoryLocation) as except_info:
        _ = mydot.Dotfiles()
    assert except_info.type is MissingRepositoryLocation


def test_tracked(fake_repo_and_work_tree):
    repo = fake_repo_and_work_tree["bare"]
    work = fake_repo_and_work_tree["worktree"]
    assert mydot.Dotfiles(repo, work).tracked == ["LICENSE", "README"]


def test_add_staged(fake_repo_and_work_tree):
    repo = fake_repo_and_work_tree["bare"]
    work = fake_repo_and_work_tree["worktree"]
    assert mydot.Dotfiles(repo, work).list_all == [
        "LICENSE",
        "README",
        "project/__init__.py",
    ]


# TODO:
# - files with spaces
# - files renamed

# vim: foldlevel=4:
