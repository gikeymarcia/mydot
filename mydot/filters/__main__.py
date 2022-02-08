from mydot.dotfiles import Dotfiles
from typing import Protocol

class Filter(Protocol):
    def __init__(self, repo: Dotfiles):
        ...


# breaking up the logic
# LiveRepo
# Filters:
# Editable(Dotfiles)
