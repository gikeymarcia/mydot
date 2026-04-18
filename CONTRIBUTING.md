# Contributing to mydot

## Project Overview

mydot is a Python CLI that manages `$HOME` dotfiles using a bare git repository
and fzf for interactive selection. The core pattern:

```
bare git repo  -->  Repository class  -->  Action classes  -->  CLI subcommands
($DOTFILES)        (queries git)          (use fzf + git)     (argparse dispatch)
```

## Project Layout

```
mydot/
  __init__.py        # exports Repository, console, __version__
  __main__.py        # CLI entry point: argparse + match/case dispatch
  repository.py      # Repository class: all git queries and cached properties
  actions.py         # Action classes: one per subcommand (EditFiles, Grep, etc.)
  editor.py          # Editor protocol + implementations (Neovim, Vim, Nano, etc.)
  clip.py            # Clipper protocol + implementations (wl-copy, xclip, xsel, pbcopy)
  console.py         # Rich console theming and text formatting
  logging.py         # Logging configuration
  exceptions.py      # Custom exceptions
tests/
  conftest.py        # Shared fixtures: fake_repo, clean_repo, submodule_repo
  test_actions.py    # Action class tests
  test_repository.py # Repository property tests
  test_submodules.py # Submodule file listing tests
  test_freshen.py    # Cache invalidation tests
  test_editor.py     # Editor discovery and search parameter tests
  test_clip.py       # Clipper discovery tests
scripts/
  venv-create.sh     # Create a .venv
  test.sh            # Run pytest with passthrough args
  test-watch.sh      # Continuous TDD with entr
  build.sh           # Build sdist + wheel, optional upload
  bump.sh            # Version bumping with bump-my-version
docs/
  development.md     # Full dev setup and workflow guide
  TODO.md            # Feature roadmap
```

## Architecture

### Repository (`repository.py`)

The central data source. It wraps a bare git repo and exposes cached properties
for different views of the file tree:

- `tracked` — committed files (excludes submodule entries)
- `list_all` — tracked + staged adds + renames + submodule files, minus deletions
- `submodule_files` — files inside submodules (depth=2)
- `modified_unstaged`, `modified_staged`, `restorables` — change sets
- `executables` — tracked files with the execute bit
- `preview_app` — best available preview command (bat > batcat > highlight > cat)

Properties use `@cached_property` and are invalidated by `freshen()`, which pops
entries from `__dict__`. Call `freshen()` after any action that mutates git state.

### Actions (`actions.py`)

Each CLI subcommand maps to an Action class with a `run()` method. The pattern:

1. Query `Repository` for a file list
2. Present it to the user with `pydymenu.fzf()`
3. If the user selects something, do the operation (open editor, run git, etc.)
4. If `None` comes back from fzf, `sys.exit()` with a message

All actions follow the `Actions` Protocol (just needs a `run()` method).

### Editor and Clipper Protocols

These use Python's `Protocol` for structural (duck) typing, not inheritance.
Each protocol defines the interface, then concrete classes implement it:

**Editor**: `open(files, search=None)` — opens files, optionally positions cursor at search term
- `Neovim`, `Vim` — support `-c /{search}` for highlighting
- `Nano` — supports `+c/{search}`
- `UserDefinedEditor` — generic fallback, no search support
- `MissingEditor` — prints files and greps when no editor found

**Clipper**: `clip(data)` — sends string to system clipboard
- `WlCopy`, `Xclip`, `Xsel`, `Pbcopy` — platform-specific implementations
  (discovery order favors Wayland first, then X11, then macOS)
- `NoApp` — prints to terminal as fallback

Discovery functions (`find_editor()`, `find_clipper()`) check `$EDITOR` env and
PATH, returning the best available implementation.

### CLI Entry Point (`__main__.py`)

Uses `argparse` with subparsers. Each subcommand maps to an action class via
`match/case`. The `Repository()` is constructed once, then passed to whatever
action runs.

## Adding a New Subcommand

Follow this pattern (using "example" as the subcommand name):

### 1. Write tests first (red phase)

```python
# tests/test_actions.py

class TestExample:
    def test_guard_clause(self, fake_repo):
        """Test behavior when precondition fails."""
        ...

    def test_happy_path(self, fake_repo, monkeypatch):
        """Test normal operation with mocked fzf."""
        ...
```

Run `scripts/test.sh` — tests should fail.

### 2. Create the Action class

```python
# mydot/actions.py

class Example(Actions):
    def __init__(self, repo: Repository):
        self.repo = repo

    def run(self) -> ...:
        selections = pydymenu.fzf(
            self.repo.list_all,
            prompt="Pick something: ",
            multi=True,
            preview=f"{self.repo.preview_app}" + " {}",
        )
        if selections is None:
            sys.exit("No selection made. Cancelling action.")
        # ... do the thing ...
```

### 3. Wire it into the CLI

```python
# mydot/__main__.py

# Add to imports:
from mydot.actions import Example

# Add subparser:
subparsers.add_parser("example", help="Description of what it does")

# Add match case:
case "example":
    Example(dotfiles).run()
```

### 4. Update README

Add the new subcommand to the usage section in `README.md`.

### 5. Run the full suite

```bash
scripts/test.sh
```

## Adding a New Editor

1. Create a class in `editor.py` implementing the `Editor` protocol
2. The class needs a `program` attribute and an `open(files, search=None)` method
3. If the editor supports search-on-open, handle the `search` parameter
4. Add the editor to the `opts` dict and `editors_to_try` list in `find_editor()`
5. Add tests in `test_editor.py` covering search and no-search cases

## Adding a New Clipper

1. Create a class in `clip.py` implementing the `Clipper` protocol
2. Needs `name` attribute and `clip(data)` method
3. Add it to the chain in `find_clipper()`
4. Add tests in `test_clip.py`

## Testing

### Fixtures

Tests use fake `Repository` objects built with `SimpleNamespace` to avoid real
git operations. Key fixtures in `conftest.py`:

- **`fake_repo`** — a repo with modified, staged, deleted, renamed, and added
  files. Use `appears_in()` to filter by tags like `"tracked"`, `"staged"`, etc.
- **`clean_repo`** — three committed files, no modifications
- **`submodule_repo`** — real git repos (bare + submodule) created in temp dirs;
  tests actual submodule file listing

### Mocking fzf

Most action tests monkeypatch `pydymenu.fzf` to return a predetermined selection
(or `None` to test the guard clause):

```python
def test_action(self, fake_repo, monkeypatch):
    monkeypatch.setattr(pydymenu, "fzf", lambda *a, **kw: ["some/file.txt"])
    # ... run the action and assert ...
```

### Running tests

```bash
scripts/test.sh              # run full suite
scripts/test.sh -x           # stop on first failure
scripts/test.sh -k "grep"    # run tests matching "grep"
scripts/test-watch.sh        # re-run on file changes (TDD mode)
```

## Releasing

1. Add an entry to `CHANGELOG.md` under a new `## [X.Y.Z] - YYYY-MM-DD` section
   summarizing user-visible changes. Do this **before** bumping — the bump
   commit should include the changelog entry.
2. `scripts/bump.sh {major|minor|patch}` — runs `bump-my-version` which
   updates `mydot/__init__.py`, `setup.py`, and `.bumpversion.toml`, and
   creates a `vX.Y.Z` tag.
3. Open an MR from a release branch to `master` (master is protected).
4. After merge: `scripts/build.sh test` to stage on test.pypi.org, verify the
   page at `https://test.pypi.org/project/mydot/X.Y.Z/`, then
   `scripts/build.sh pypi` for the real release.

`~/.pypirc` needs `[testpypi]` and `[pypi]` sections (username `__token__`,
password = token). The build script uploads via `-r testpypi` / `-r pypi`
aliases, so twine's built-in endpoints are used — do **not** override with
`--repository-url` or custom repo sections pointing at browse URLs.

## Style Notes

- Use `match/case` for dispatch (Python 3.10+)
- Prefer `sys.exit("message")` over raising exceptions for user-facing errors
- Use `@cached_property` for expensive git queries; invalidate with `freshen()`
- Action constructors take a `Repository` and optionally an Editor/Clipper
  (for testability via dependency injection)
- Protocol classes use `...` (Ellipsis) as the method body, not
  `raise NotImplementedError`
- Keep the fzf selection pattern consistent: query -> fzf -> None check -> action
