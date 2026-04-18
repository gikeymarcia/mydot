# mydot -- A Python module for managing dotfiles

Super-charged version of the [Atlassian][atlassian] approach to managing
dotfiles using a bare git repo + [`fzf`][fzf] magic! Quickly edit files, add
changes, run scripts, grep through dotfiles, or discard work-tree changes with
ease.

## Quick Start

1. **Install dependencies:**

    ```bash
    sudo apt install fzf git    # Ubuntu/Debian
    brew install fzf git        # MacOS/Homebrew
    ```
1. **Configure shell:** At the bottom of your `~/.bashrc` or `~/.zshrc` add:

    ```bash
    export DOTFILES="$HOME/.config/dotfiles"
    alias config='/usr/bin/git --git-dir=$DOTFILES --work-tree=$HOME'
    ```

    _what and why?_:

    - `DOTFILES`: variable pointing to your local `--bare` dotfiles repository
    - `config`: git alias to directly address the `--bare` dotfiles repository

2. **Initialize dotfiles repository:**

    ```bash
    # reload shell configu
    source ~/.bashrc            # if using bash
    source ~/.zshrc             # if using zsh

    mkdir -pv $DOTFILES         # create directory
    git init --bare $DOTFILES   # initialize --bare git repository
    ```

3. **Install** `mydot` and disable viewing of untracked files

    ```bash
    pip install --user mydot    # if using pip
    pipx install mydot          # if using pipx
    mydot git config --local status.showUntrackedFiles no
    ```

3. **Add files** to your dotfiles repo

    ```bash
    mydot git add ~/.vimrc ~/.tmux.conf ~/.bashrc ~/.bash_aliases ~/.zshrc
    mydot git commit -m "the journey of a thousand miles begins with one step"
    ```

    _protip:_ You can use all your regular git commands, including aliases, when
    calling `mydot git`

4. **Feel the power** with `mydot` (and the pre-installed alias `d.`)

    ```bash
    d. edit         # modify tracked files in your $EDITOR (tab in fzf for multiselect)
    d. add          # choose which modified files to stage for commit
    d. git commit   # commit changes

    d. grep zfs     # find all files with lines containing the string zfs
    d. grep zfs$    # works with regex too! e.g, zfs$ something.*var ^$
    d. grep -E "zfs|ext4" # extended regexp

    d. run          # run any executable script in your dotfiles repo
    d. status       # see the state of your repo
    d. ls           # list all files under version control

    d. export       # make a tarball of your dotfiles + bare git repo
    d. clip         # put file paths into the clipboard

    d. restore      # remove files from staging area
    d. discard      # discard unstaged changes from work tree

    d. fzf          # select files and print paths to stdout (for piping)
    d. history      # browse and compare file history
    d. cd           # navigate to a dotfile's directory in a subshell

    d.              # see the help message detailing available commands
    ```

## Submodule Support

If your dotfiles repo contains git submodules (e.g., `~/.config/tmux`), mydot
will include their tracked files in `edit`, `fzf`, `clip`, `grep`, `ls`, `cd`,
and `export` (up to 2 levels deep).

**Known limitation:** `d. history` will list submodule files but cannot show
their per-file commit history. The outer repo only tracks the submodule pointer,
not individual file changes within the submodule.

## Going Deeper

### Customizing `d. cd`

By default `d. cd` lists the directory with `ls -lA --color=auto` before
opening the subshell. Set `MYDOT_CD_CMD` to use a different listing command:

```bash
export MYDOT_CD_CMD="eza -la"   # use eza
export MYDOT_CD_CMD="tree -L 2" # use tree
```

### Useful aliases

```bash
alias es="mydot edit"     # quick select a file to edit
alias rs="mydot run"      # quick select a script to run
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
[template]: <https://github.com/gikeymarcia/super-python-project-template>
"Super Python Project Template @ GitHub"
