---
author: Mikey Garcia
date: 2022-03-24 22:36
title: Asciinema
---

I am going to record some demos of `mydot` features using the `asciinema` tool.
The package is included in the `requirements_dev.txt` and can be used as
follows.

```bash
# record terminal to file
asciinema rec cool-feature
# end recording with Ctrl+d

# playback the recording
asciinema play cool-feature

# re-record terminal to file
asciinema rec --overwrite cool-feature
```

[Full documentation][usage] is available for more advanced uses.

[usage]: <https://asciinema.org/docs/usage>
"Usage - asciinema"
