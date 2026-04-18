# Mikey Garcia, @gikeymarcia
# https://github.com/gikeymarcia/mydot

import shutil
import subprocess
from typing import Protocol


class Clipper(Protocol):
    name: str

    def clip(self, data: str) -> None:
        """Copy data to clipboard."""
        ...

    def success(self, data: str, location: str = "clipboard"):
        """Print a success message after using a Clipper"""
        print(f"Copied file path(s) to {location}:")
        print(f"'{data}'")

    def has_app(self) -> bool:
        """Return true if this application is on the system, othewise false."""
        return False if shutil.which(self.name) is None else True


class Xclip(Clipper):
    name = "xclip"

    def clip(self, data: str):
        subprocess.run(["xclip", "-selection", "clipboard"], input=data.encode("utf-8"))
        self.success(data)


class Xsel(Clipper):
    name = "xsel"

    def clip(self, data: str):
        subprocess.run(["xsel", "-ib"], input=data.encode("utf-8"))
        self.success(data)


class WlCopy(Clipper):
    name = "wl-copy"

    def clip(self, data: str):
        subprocess.run(["wl-copy"], input=data.encode("utf-8"))
        self.success(data)


class Pbcopy(Clipper):
    name = "pbcopy"

    def clip(self, data: str):
        subprocess.run(["pbcopy"], input=data.encode("utf-8"))
        self.success(data)


class NoApp(Clipper):
    name = "missing"

    def clip(self, data: str):
        print("ERROR: Could not find a clipboard application:")
        print(f"{data}")


def find_clipper() -> Clipper:
    """
    Find a suitable clipboard app and return as a Clipper object.

    Checks: wl-copy > xclip > xsel > pbcopy > terminal print (fallback)
    """
    for option in [WlCopy(), Xclip(), Xsel(), Pbcopy()]:
        if option.has_app():
            return option
    else:
        return NoApp()


# vim: foldlevel=0:
