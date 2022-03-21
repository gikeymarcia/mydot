# standard library
from pathlib import Path

import pytest

import mydot
from mydot.exceptions import MissingRepositoryLocation


def test_import_module():
    assert mydot


@pytest.fixture
def defined_dot():
    dots = Path.home() / ".config/dotfiles"
    work = Path.home()
    return mydot.Repository(local_bare_repo=dots, work_tree=work)


def test_defined_repo_and_work_tree(defined_dot):
    assert defined_dot.bare_repo == Path.home() / ".config/dotfiles"
    assert defined_dot.work_tree == Path.home()


def test_env_defined_repo_with_default_work_tree(monkeypatch, tmpdir):
    monkeypatch.setenv("DOTFILES", str(tmpdir))
    default_vals = mydot.Repository()
    assert default_vals.bare_repo == Path(str(tmpdir))
    assert default_vals.work_tree == Path.home()


def test_missing_DOTFILES_in_env(monkeypatch):
    monkeypatch.delenv("DOTFILES", raising=False)
    with pytest.raises(MissingRepositoryLocation) as except_info:
        _ = mydot.Repository()
    assert except_info.type is MissingRepositoryLocation


# vim: foldlevel=1:
