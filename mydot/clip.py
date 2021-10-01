# Mikey Garcia, @gikeymarcia
# https://github.com/gikeymarcia/mydot

from typing import Protocol
from subprocess import run
from shutil import which
from mydot.exceptions import MissingProgram


class Clipper(Protocol):
    name: str

    def clip(self, data: str):
        raise NotImplementedError

    def success(self, data: str, location: str = "clipboard"):
        print(f"Copied file path(s) to {location}:")
        print(f"'{data}'")

    def has_app(self) -> bool:
        return False if which(self.name) is None else True


class Xclip(Clipper):
    name = "xclip"

    def clip(self, data: str):
        run(["xclip", "-selection", "clipboard"], input=data.encode("utf-8"))
        self.success(data)


class Xsel(Clipper):
    name = "xsel"

    def clip(self, data: str):
        run(["xsel", "-ib"], input=data.encode("utf-8"))
        self.success(data)


class Pbcopy(Clipper):
    name = "pbcopy"

    def clip(self, data: str):
        run(["pbcopy"], input=data.encode("utf-8"))
        self.success(data)


class NoApp(Clipper):
    name = "missing"

    def clip(self, data: str):
        print("ERROR: Could not find a clipboard application:")
        print(f"{data}")


def find_clipper() -> Clipper:
    """
    Find a suitable clipboard app and return as a Clipper object.

    Checks: xclip > xsel > pbcopy > terminal print (fallback)
    """
    for option in [Xclip(), Xsel(), Pbcopy()]:
        if option.has_app():
            return option
    else:
        return NoApp()


# vim: foldlevel=0:
