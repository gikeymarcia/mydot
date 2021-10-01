# Mikey Garcia, @gikeymarcia
# https://github.com/gikeymarcia/mydot

from pathlib import Path
from typing import List


def script_plus_args(script: Path) -> List[str]:
    """Optionally add arguements to a selected script."""
    print("\nAdd script arguments, press ENTER to run\n")
    if len(scr_args := input(f"{script} ").strip()) > 0:
        return [str(script)] + scr_args.split()
    else:
        return [str(script)]
