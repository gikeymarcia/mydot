## Mydot TODO list

### Chores / Catch Up

- [x] Migrate from bump2version to [bump-my-version](https://github.com/callowayproject/bump-my-version)
- [x] Replace tools.sh with scripts/ directory

### Features

- [x] history subcommand
    - `git log --oneline -- bootstrap.yml | awk '{print $1'} | fzf --preview="git show {}:bootstrap.yml"'`
    - flow
        1. pick file
        2. get list of hashes
        3. fzf picker with preview of each version
        4. Upon selection open file in split view with current version
- [x] fzf: selector meant to send through a pipeline `d. fzf | xargs ...`

### Future

- [ ] Make `d. history` work for submodule files (query the submodule's own git log)
- [ ] Record asciinema demos for each subcommand
- [ ] Replace `python -m mydot` usage hints with `d.` — it's the alias
      everyone actually uses. Touches `mydot/__main__.py` argparse `prog`,
      `docs/watch.md`, `docs/ideas.md`, and the `docs/bugs/0001` note.
