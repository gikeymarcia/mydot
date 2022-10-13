---
title: Missing Core Features
date: 2022-10-13 10:38
author: Mikey Garcia, @gikeymarcia
---

1. Support for dealing with conflicted files after attempted merges.

For Example, `git status -sb`

```
## laptop...private/laptop
UU ../../../.notes/linux-sysadmin/proxmox.md
```

When I run `d. -a` the conflicted file should show up as available to add. There
should also be a `d. --conflict` which will give me a selector to open files in
an `$EDITOR` and after the editor closes it will ask if I'd like to stage the
file now. Potentially even search for diff markers and only ask if they're gone.
