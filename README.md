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
1. **Configure shell:** At the bottom of your `~/.bashrc` or `~/.zshhrc` add:

    ```bash
    export DOTFILES="$HOME/.config/dotfiles"
    alias config='/usr/bin/git --git-dir=$DOTFILES --work-tree=$HOME'
    ```

    _what and why?_:

    - `DOTFILES`: variable pointing to your local `--bare` dotfiles repository

2. **Initialize dotfiles repository:** Reload shell config with `source ~/.bashrc` 
    or `source ~/.zshhrc` then:

    ```bash
    mkdir -pv $DOTFILES         # create directory
    git init --bare $DOTFILES   # initialize the repository
    ```

3. **Install** `mydot` and disable viewing of untracked files

    ```bash
    pip install --user mydot
    mydot git config --local status.showUntrackedFiles no
    ```

3. **Add files** to your dotfiles repo

    ```bash
    mydot git add ~/.vimrc ~/.tmux.conf ~/.bashrc ~/.bash_aliases ~/.zshrc
    mydot git commit -m "the journey of a thousand miles begins with one step"
    ```

    _protip:_ You can use all your regular git commands, including aliases, when
    calling `d. git`

4. **Feel the power** with `mydot` (and the pre-installed alias `d.`)

    ```bash
    d. -e       # choose file(s) to open in $EDITOR
    d. -a       # choose modified files to add file(s) to staging area
    d. -r       # select an executable file to run
    d. -g       # grep through tracked dotfiles and open from matches
    d. -s       # see the state of your repo
    d. -l       # list all files under version control

    d. --export     # make a tarball of your dotfiles + bare git repo
    d. --clip       # put file paths into the clipboard

    d. --restore    # remove files from staging area
    d. --discard    # discard unstaged changes from work tree

    d.          # see the help message whihc details available commands
    ```

## Going Deeper

### Useful aliases

```bash
alias es="mydot --edit"     # quick select a file to edit
alias rs="mydot --run"      # quick select a script to run
```

If you ever run into an issue where the `mydot` CLI is reading flags meant for 
`mydot git` you can fallback to the `config` alias from step 1 which acts as a 
special git command that only applies for the dotfiles repo.

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
