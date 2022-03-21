# Project Ideas

- [ ] `d. friend` allow me to follow the dotfiles of other users
    -  You can follow each other and serve as one another's backups and share
       useful
    - tools and practices.
- [ ] `init` Bootstrap a machine without a current dotfiles repo
    - Add `d.` alias and `$DOTFILES` variable
        - `>> .zshrc` AND `>> ~/.bashrc`
            - `export DOTFILES="$HOME/.config/dotfiles/"`
            - `alias d.="python -m mydot"`
            - `export DOTFILES="$HOME/.config/dotfiles/"`
            - `alias d.="python -m mydot"`

        - initialize the repo (README step 2)
    - `git config --local status.showUntrackedFiles no`
    - install dependencies (fzf, git)
        - [ ] Debian
        - [ ] Arch
        - [ ] RHEL
        - what else?

- [ ] `--dir` get directory selection

    ```bash
    alias d.j='source move-term.sh python -m mydot --dir'
    ```

    - When used with `move-term.sh` I'll be able to **jump** to any folder
    containing one of my tracked dotfiles.

- [ ] `--private` build up a filter of files marked 'private'
  - hide from previews
  - default hide from --tar
  - consider relation to other features
  - put folder in `$XDG_CONFIG_HOME/mydot`

- [ ] `--import` Pass the location of a dotfiles repository and pull it's
contents down into the current user's `$HOME`
    - attempt a `git checkout`; move conflicted files into
    `~/.backup-dotfiles/` folder if conflicts are found.
      - Maintain directory structure relative to work-tree and after the import
        tell the user which files were moved to backups. Ask `Y/n` if they'd
        like to restore any of the backed up versions. If Yes, then fzf select
        which files to move from backup to live. Show diff as preview when
        selecting.

- [  ] `--rofi` / `--dmenu` options for the `--edit` command which gives a GUI
  quick selector
    - Potential idea: allow the same for the `--run` command but without the
      added logic of being able to pass parameters to the command.

- [ ] `--branch` switch to or checkout branches

- [ ] Use the [`tarfile` module][tarfile] for the `--tar` command


```
# establish/switch to a context which can turn on/off/rollback other contexts
d context laptop

d context laptop
```

### Done

- [X] `--clip` search for files and put them into the clipboard
    - optionally, put files into the tmux buffer if within tmux

[tarfile]: <https://docs.python.org/3/library/tarfile.html#module-tarfile>
"tarfile -- Read and write tar archive files"

### Spitballing

```bash
# fzf files from current working directory
d. -A --add-selector
```


- fzf screen for actions (on, off, versions)
    - screen to choose contexts
      - e.g, tmux nvim sound i3 python
    - Once selected you can turn the configs on, off, or choose an
      alternative version of it
