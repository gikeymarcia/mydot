# mydot -- A Python Module for managing dotfiles

## Quick Start

1. Configure `bash` shell:

    ```bash
    # Environment variable specifying where to store dotfiles
    export DOTFILES="$HOME/.config/dotfiles"
    alias config="/usr/bin/git --git-dir=$DOTFILES --work-tree=$HOME"
    ```
2. Initialize dotfiles repository

    ```bash
    # Initialize repository
    mkdir -pv $DOTFILES
    git init --bare $DOTFILES
    ```

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
    python -m mydot --help
    python -m mydot --status
    python -m mydot --edit
    python -m mydot --add
    ```

### Source of Truth

This project is available on [GitHub][github] and [GitLab][gitlab]. Each push to 
`master` automatically goes to both so choose whichever platform you prefer.

[github]: <https://github.com/gikeymarcia/mydot>
"Follow and Contribute on GitHub"
[gitlab]: <https://gitlab.com/gikeymarcia/mydot>
"Follow and Contribute on GitLab"
