# mydot -- A Python Module for managing dotfiles

Super-charged version of the [Atlassian][atlassian] approach to managing 
dotfiles using a bare git repo + [`fzf`][fzf] magic!

## Quick Start

1. **Configure shell:** At the bottom of your `~/.bashrc` add:

    ```bash
    export DOTFILES="$HOME/.config/dotfiles"
    alias d.="python -m mydot"
    ```

    _what and why?_:

    - `DOTFILES`: variable pointing to your local `--bare` dotfiles repository
    - `d.` alias to invoke `mydot`'s command line interface

2. **Initialize dotfiles repository:** First open a new shell or `source ~/.bashrc`{.bash} then:

    ```bash
    mkdir -pv $DOTFILES         # create directory
    git init --bare $DOTFILES   # initialize the repository
    ```

3. **Install** `mydot`, `fzf`, and disable viewing of untracked files

    ```bash
    pip install --user mydot
    sudo apt install fzf -y
    d. git config --local status.showUntrackedFiles no
    ```

3. **Add files** to your dotfiles repo

    ```bash
    d. git add ~/.vimrc ~/.tmux.conf ~/.bashrc ~/.bash_aliases
    d. git commit -m "the journey of a thousand miles begins with one step"
    ```

    _protip:_ `d. git` gives you full control and lets you do anything available from the `git` command.

4. **Feel the power** with `mydot`

    ```bash
    d. --edit   # choose a file to open in $EDITOR
    d. --add    # add changed files to staging area
    d. --run    # select an executable file to run
    d. --grep   # grep through tracked dotfiles and pick from matches
    d. --restore # remove files from staging area

    d. --tar    # make a tarball of your dotfiles
    d. --status # see the state of your repo
    d. --ls     # list all files under version control

    d. --help   # see more detials about available commands
    ```

## Going Deeper

### Useful aliases

```bash
alias es="python -m mydot --edit" # quick select a file to edit
alias rs="python -m mydot --run" # quick select a script to run
```

### Source of Truth

This project is available on [GitHub][github] and [GitLab][gitlab]. Each push 
to `master` automatically goes to both so choose whichever platform you prefer. 
All releases are published to [PyPi][pypi]

[github]: <https://github.com/gikeymarcia/mydot>
"Follow and Contribute on GitHub"
[gitlab]: <https://gitlab.com/gikeymarcia/mydot>
"Follow and Contribute on GitLab"
[pypi]: <https://pypi.org/project/mydot/>
"mydot project homepage on PyPi.org"
[atlassian]: <https://www.atlassian.com/git/tutorials/dotfiles>
"The best way to store your dotfiles: A bare Git repository"
[fzf]: <https://github.com/junegunn/fzf>
"A command-line fuzzy finder"
