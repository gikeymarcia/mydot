#!/usr/bin/env python3
# Mikey Garcia, @gikeymarcia
# https://github.com/gikeymarcia/mydot

import pytest
from mydot.bootstrap import CreateRepo
from mydot.exceptions import RepoAlreadyExists
from pathlib import Path
from os import getenv


@pytest.fixture
def empty_init(tmp_path, monkeypatch):
    """Make fake env to initalize dotfiles repo."""
    # tell it to create (make dotfiles dir and init)
    # if it doesn't exist
    # find bashrc
    # include variable definition
    # find zshrc (lookup ZDOTDIR)

    xdg: Path = tmp_path / ".config"
    dots: Path = xdg / "dotfiles"
    bashrc: Path = tmp_path / ".bashrc"
    zshrc: Path = tmp_path / ".zshrc"
    for file in [bashrc, zshrc]:
        file.write_text(f"# fake {file.name} file")

    monkeypatch.setenv("HOME", str(tmp_path))
    monkeypatch.setenv("XDG_CONFIG_HOME", str(xdg))
    monkeypatch.delenv("DOTFILES", raising=False)
    return {
        "xdg": xdg,
        "dots": dots,
        "bashrc": bashrc,
        "zshrc": zshrc,
        "home": str(tmp_path),
        "create": CreateRepo(),
    }


def test_instantiate_creator():
    assert CreateRepo


def test_bare_fixture_setup(empty_init):
    "Simple case: No DOTFILES var, XDG set, .bashrc exists, .zshrc exists"
    # correct env setup
    assert getenv("DOTFILES", None) == None
    assert getenv("XDG_CONFIG_HOME", None) == str(empty_init["xdg"])
    assert getenv("HOME", None) == str(empty_init["home"])
    # bashrc and zshrc exist and have simple filler content
    for rc_file in [empty_init["bashrc"], empty_init["zshrc"]]:
        assert rc_file.is_file()
        assert len(rc_file.read_text().split("\n")) == 1
    creator = empty_init["create"]
    # pre-creation: repo does not exist
    assert creator.repo == empty_init["dots"]
    assert creator.repo.is_dir() == False
    assert creator.bare_repo_exists() == False


def test_simple_init(empty_init):
    """Test bootstrap adds to shellrc files and makes the bare repo."""
    creator = empty_init["create"]
    # create dotfiles
    creator.bootstrap_dotfiles()
    assert creator.repo.is_dir() == True
    assert creator.bare_repo_exists() == True
    for rc_file in [empty_init["bashrc"], empty_init["zshrc"]]:
        assert len(rc_file.read_text().split("\n")) == 3
        print(rc_file.read_text())


def test_existing_repo(empty_init):
    populate = CreateRepo()
    populate.bootstrap_dotfiles()
    with pytest.raises(RepoAlreadyExists) as except_info:
        empty_init["create"].bootstrap_dotfiles()
    assert except_info.type is RepoAlreadyExists
