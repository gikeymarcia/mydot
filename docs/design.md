# Project Design Goals

`alias d="python -m mydot"`{.bash}

#### Commands

```bash
# act as transparent pass-through for git commands
# Honor git aliases! `shell=True`? How to get env to activate aliases...
d status
d add
d log

# fzf files from current working directory
d add - 

# establish/switch to a context which can turn on/off/rollback other contexts
d context laptop

d context laptop

# fzf screen for actions (on, off, versions)
# screen to choose contexts
#   tmux nvim sound i3 python
# Once selected you can turn the configs on, off, 
#   or choose an alternative version of it

# You can follow each other and serve as one another's backups and share useful
# tools and practices.

```
