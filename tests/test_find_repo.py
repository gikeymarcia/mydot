# standard library
from pathlib import Path
import subprocess as sp

# my project
import mydot

# from pypi
import pytest


@pytest.fixture
def fake_repo_and_work_tree(tmp_path):
    repo = tmp_path / "bare"
    work = tmp_path / "work"
    repo.mkdir()
    work.mkdir()
    print(f"bare repo: {repo}", f"work-tree: {work}", sep="\n")
    # alias config='/usr/bin/git --git-dir=$DOTFILES --work-tree=$HOME'
    create_cmd = ["git", "init", "--bare", repo]
    a, b, c = (work / "greetings", work / "code", work / "README")
    sp.run(create_cmd)
    sp.run(["ls", "-la", work])
    sp.run(["ls", "-la", repo])
    return {"repo": repo, "worktree": work, "create": create_cmd}


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
    with pytest.raises(KeyError) as except_info:
        _ = mydot.Dotfiles()
    assert except_info.type is KeyError


def test_fixture_status(fake_repo_and_work_tree):
    repo = fake_repo_and_work_tree["repo"]
    work = fake_repo_and_work_tree["worktree"]
    create = fake_repo_and_work_tree["create"]
    assert False
