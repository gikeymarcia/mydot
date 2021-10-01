# https://realpython.com/pypi-publish-python-package/#a-small-python-package
from pathlib import Path
from setuptools import setup, find_packages

README = (Path(__file__).parent / "README.md").read_text()

# https://setuptools.readthedocs.io/en/latest/setuptools.html#basic-use
setup(
    name="mydot",
    version="0.5.0",
    description="Manage and edit $HOME dotfiles using Python + git = <3",
    long_description=README,
    long_description_content_type="text/markdown",
    url="https://github.com/gikeymarcia/mydot",
    author="Mikey Garcia",
    author_email="gikeymarcia@gmail.com",
    license="GPL-3.0",
    packages=find_packages(exclude="tests"),
    install_requires=["pydymenu>=0.5.0", "rich"],
)
