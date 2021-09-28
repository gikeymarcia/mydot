# Project Ideas


- [ ] `--init` Boostrap a machine without a current dotfiles repo
    - install dependencies (fzf, git)
        - [ ] Ubuntu
        - [ ] Arch
        - [ ] RHEL
        - what else?
    - Add `d.` alias and `$DOTFILES` variable to `~/.bashrc`
        - make it work with `zsh` too. Figure out how.
    - initialize the repo (README step 2)
    - `git config --local status.showUntrackedFiles no`

- [ ] `--import` Pass the location of a dotfiles repository and pull it's 
  contents down into the current user's `$HOME`
    - attempt to do a `git checkout` and if there are any conflicts move those 
      files into a `~/.backup-dotfiles/` folder.
      - Maintain directory structure relative to work-tree and after the import 
        tell the user which files were moved to backups. Ask `Y/n` if they'd 
        like to restore any of the backed up versions. If Yes, then fzf select 
        which files to move from backup to live. Show diff as preview when 
        selecting.
  

- [ ] `--clip` search for files and put them into the clipboard
    - optionally, put files into the tmux buffer if within tmux

- [  ] `--rofi` / `--dmnu` options for the `--edit` command which gives a GUI 
  quick selector
    - Potential idea: allow the same for the `--run` command but without the 
      added logic of being able to pass parameters to the command.
