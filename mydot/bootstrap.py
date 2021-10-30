#!/usr/bin/env python3
# Mikey Garcia, @gikeymarcia
# https://github.com/gikeymarcia/dotfiles

from os import getenv, chdir
from pathlib import Path
from subprocess import run
from typing import Optional

from mydot.exceptions import RepoAlreadyExists


class CreateRepo:
    def __init__(self):
        self.home: Path = self.resolve_home()
        self.repo: Path = self.resolve_dotfiles_repo()

    def resolve_dotfiles_repo(self) -> Path:
        """Figure out where to put a dotfiles repo

        Default location is $XDG_CONFIG_HOME/dotfiles
        if XDG_CONFIG_HOME is not set use $HOME/.config/dotfiles
        """
        env_xdg = getenv("XDG_CONFIG_HOME", None)
        xdg = Path(env_xdg) if env_xdg else self.home / ".config"
        dots = xdg / "dotfiles"
        return dots

    def resolve_home(self) -> Path:
        env_home = getenv("HOME", None)
        if env_home:
            return Path(env_home)
        else:
            return Path.home()

    def bootstrap_dotfiles(self):
        if not self.repo.is_dir():
            self.repo.mkdir(parents=True)
        if self.bare_repo_exists() == False:
            run(["git", "init", "--bare", self.repo], capture_output=True)
        else:
            raise RepoAlreadyExists(f"There is already a bare repo @ {self.repo}")
        after_var = self.repo.relative_to(self.home)
        alias = 'alias d.="python -m mydot"'
        variable = f'export DOTFILES="$HOME/{after_var}/"'
        for shellrc in [self.bashrc, self.zshrc]:
            if shellrc:
                with shellrc.open("a") as f:
                    f.write("\n" + variable)
                    f.write("\n" + alias)

    @property
    def zshrc(self) -> Optional[Path]:
        rc_file = self.home / ".zshrc"
        return rc_file if rc_file.is_file() else None

    @property
    def bashrc(self) -> Optional[Path]:
        rc_file = self.home / ".bashrc"
        return rc_file if rc_file.is_file() else None

    def bare_repo_exists(self) -> bool:
        if self.repo.is_dir():
            chdir(self.repo)
            proc = run(
                ["git", "rev-parse", "--is-bare-repository"], capture_output=True
            )
            return True if proc.returncode == 0 else False
        else:
            return False


# PSEUDOCODE:
# find .bashrc
# compute DOTFILES location
# check if it is already a repo
# else:
