# mydot -- A Python Module for managing dotfiles

## Quick Start

1. Configure `bash`

    ```bash
    # add to the bottom of your `~/.bashrc`:
    export DOTFILES="$HOME/.config/dotfiles"
    alias config="/usr/bin/git --git-dir=$DOTFILES --work-tree=$HOME"
    alias d.="python -m mydot"
    ```

    First we define a variable which will point to where our dotfiles are stored then make two aliases. 

    - `config`: interact with the repo directly
    - `d.` invoke the module's command line interface

2. Initialize dotfiles repository

    ```bash
    mkdir -pv $DOTFILES
    git init --bare $DOTFILES
    ```

    Create the directory (and any parents) then initialize the bare repo

3. Confirm and configure dotfiles repo

    ```bash
    # Confirm working dotfiles alias
    config status
    # Disable display of untracked files
    config config --local status.showUntrackedFiles no
    # Confirm change
    config status
    # Add files to track using Git
    config add -v ~/.vimrc ~/.tmux.conf ~/.bashrc ~/.bash_aliases
    ```

4. Get powerful with `mydot`

    ```bash
    python -m pip install --user mydot
    # try out the commands
    d. --help
    d. --edit
    d. --add
    d. --restore
    d. --status
    d. --ls
    ```

### Source of Truth

This project is available on [GitHub][github] and [GitLab][gitlab]. Each push to 
`master` automatically goes to both so choose whichever platform you prefer.

[github]: <https://github.com/gikeymarcia/mydot>
"Follow and Contribute on GitHub"
[gitlab]: <https://gitlab.com/gikeymarcia/mydot>
"Follow and Contribute on GitLab"
