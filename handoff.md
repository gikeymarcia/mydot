## Handoff — mydot 0.9.x release cycle

### State at handoff

- Version: 0.9.2 (see `mydot/__init__.py`, `setup.py`, `.bumpversion.toml`)
- Tests: 86 passing under `.venv/bin/python -m pytest`
- Release branch: `v0.9.2-release` (single squashed commit from origin/master
  at 0.9.1). MR awaiting user-driven merge in the GitLab UI.
- Test PyPI upload confirmed live at
  https://test.pypi.org/project/mydot/0.9.2/ — final PyPI push happens after
  merge via `scripts/build.sh pypi`.

### Architectural decisions made this cycle

1. **Repository / Action / Protocol pattern is the contract**
   - `Repository` (repository.py) is the only place that talks to git. Cached
     properties expose different file-set views; `freshen()` pops `__dict__`
     entries to invalidate after mutations.
   - Each subcommand is an `Action` class in `actions.py` with a single `run()`
     method. Constructors take a `Repository` (and optionally an Editor/Clipper)
     for dependency-injected testability.
   - `Editor` and `Clipper` are `typing.Protocol` classes (structural typing).
     Method bodies are `...`, not `raise NotImplementedError` — this was a
     style fix applied across the protocols.

2. **Submodule support is intentionally partial**
   - `list_all` (used by edit/fzf/clip/grep/ls/export/history pickers) includes
     submodule files via `submodule_files` (depth=2 ls-tree walk).
   - `modified_*` and `restorables` (used by add/restore/discard) deliberately
     do **not** descend into submodules — git status treats submodules as atomic
     entries and these mutating actions can't operate on inner files anyway.
   - Known limitation: `d. history` cannot show per-file history for submodule
     files because the outer repo only tracks the submodule pointer. Documented
     in README "Submodule Support" and in `docs/TODO.md` Future section.

3. **Tooling moves**
   - `bump2version` → `bump-my-version`, config in `.bumpversion.toml` (the old
     `.bumpversion.cfg` was removed to silence the deprecation warning).
   - `python setup.py sdist bdist_wheel` → `python -m build` in `scripts/build.sh`.
     `build` was added to `requirements_dev.txt`.
   - `tools.sh` was retired in favor of `scripts/` (venv-create.sh, test.sh,
     test-watch.sh, build.sh, bump.sh).
   - Removed unused dev deps: ipdb, pynvim, asciinema (asciinema captured in
     TODO.md as a future "record demos" item).

4. **CLI ergonomics**
   - `-v` / `--version` flag added via argparse `version` action, sourced from
     `mydot.__version__`. Output format is plain `v{version}` (no `%(prog)s`
     prefix).
   - Git passthrough log line moved from INFO → DEBUG to silence noise during
     normal use.

6. **PyPI upload config**
   - `scripts/build.sh` uploads via `-r testpypi` / `-r pypi` (standard
     `.pypirc` aliases), not `--repository-url`. A custom repo section with
     the *browse* URL (e.g. `https://test.pypi.org/project/mydot/`) will
     silently no-op — the upload endpoint is `https://test.pypi.org/legacy/`,
     which twine already knows for the `testpypi` alias.
   - `~/.pypirc` on the push host needs two sections — `[testpypi]` and
     `[pypi]` — each with `username = __token__` and a real token.

5. **Style fixes applied**
   - `src_repo` → `repo` in all Action constructors (and docs/CONTRIBUTING.md
     examples).
   - Removed ASCII art / stale TODO comments from repository.py and editor.py.
   - `import subprocess as sp` → `import subprocess` in clip.py.

### SemVer rationale for 0.9.0

New `fzf` and `history` subcommands are additive; no existing CLI surface
changed. Minor bump was correct. Patch bumps (.1, .2) covered the INFO log fix
and the build-script fix respectively.

### What's outstanding

- Merge `v0.9.2-release` → `master` via GitLab MR (master is protected on
  gitlab.gtribe.casa; CLI push is rejected).
- After merge, tag `v0.9.2` on the merged commit and run
  `scripts/build.sh pypi` to publish to real PyPI. Confirm
  `twine check dist/*` is clean first.
- `docs/TODO.md` Future section:
  - Make `d. history` work for submodule files (query the inner repo's git log)
  - Record asciinema demos for each subcommand
- `CHANGELOG.md` was reconstructed in this cycle back to 0.6.0. Keep it
  current going forward — add an entry *before* each version bump.

### How to come back up

1. `bash scripts/venv-create.sh` to recreate `.venv/`
2. `scripts/test.sh` — expect 86 passing
3. Read `CONTRIBUTING.md` for the Repository → Action → Protocol pattern and
   the "Adding a New Subcommand" recipe (red-green TDD).
