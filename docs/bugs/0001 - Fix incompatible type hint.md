# Bug 1

When my brother tried to run `python -m mydot` he got this error code. 

```
Traceback (most recent call last):
  File "/usr/lib/python3.8/runpy.py", line 185, in _run_module_as_main
    mod_name, mod_spec, code = _get_module_details(mod_name, _Error)
  File "/usr/lib/python3.8/runpy.py", line 144, in _get_module_details
    return _get_module_details(pkg_main_name, error)
  File "/usr/lib/python3.8/runpy.py", line 111, in _get_module_details
    __import__(pkg_name)
  File "/home/david/.local/lib/python3.8/site-packages/mydot/__init__.py", line 1, in <module>
    from mydot.dotfiles import Dotfiles
  File "/home/david/.local/lib/python3.8/site-packages/mydot/dotfiles.py", line 15, in <module>
    from pydymenu import fzf
  File "/home/david/.local/lib/python3.8/site-packages/pydymenu/__init__.py", line 1, in <module>
    from pydymenu.rofi import rofi
  File "/home/david/.local/lib/python3.8/site-packages/pydymenu/rofi.py", line 10, in <module>
    from pydymenu.system import has_bin, newline_joined_bytestream, process_stdout
  File "/home/david/.local/lib/python3.8/site-packages/pydymenu/system.py", line 17, in <module>
    def process_stdout(proc: CompletedProcess) -> Union[list[str], None]:
TypeError: 'type' object is not subscriptable
```

After some poking around I found the issue was the use of the `list[str]` type hint. Being able to use the builtin `list` for the hint was only added in Python 3.9. For earlier versions you need to import `List` from `typing`. _Example:_

```python
from typing import List

my_strings : List[str] = ["hut", "two", "three"]
```
