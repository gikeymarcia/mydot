## Mydot TODO list

### Chores / Catch Up

- [ ] Migrate from bump2version to [bump-my-version](https://github.com/callowayproject/bump-my-version)

### Features

- [ ] history subcommand
    - `git log --oneline -- bootstrap.yml | awk '{print $1'} | fzf --preview="git show {}:bootstrap.yml"'`
    - flow
        1. pick file
        2. get list of hashes
        3. fzf picker with preview of each version
        4. Upon selection open file in split view with current version
- [ ] fzf: selector meant to send through a pipeline `d. fzf | xargs ...`
