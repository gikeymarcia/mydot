# Development Guide

## Setup

Create a virtual environment and install all dependencies (runtime + dev + editable install of mydot):

```bash
scripts/venv-create.sh
source .venv/bin/activate
```

## Running Tests

Run the full test suite:

```bash
scripts/test.sh
```

Pass extra pytest flags as needed:

```bash
scripts/test.sh -x            # stop on first failure
scripts/test.sh -k "submodule" # run only matching tests
```

### Continuous Testing (TDD)

Re-runs tests automatically on file changes (requires `entr`):

```bash
scripts/test-watch.sh
```

## Version Bumping

Uses [bump-my-version](https://github.com/callowayproject/bump-my-version). Config lives in `.bumpversion.toml` and updates `setup.py` + `mydot/__init__.py`.

Show current version and available bumps:

```bash
scripts/bump.sh
```

Bump a specific part:

```bash
scripts/bump.sh patch     # 0.8.0 → 0.8.1
scripts/bump.sh minor     # 0.8.0 → 0.9.0
scripts/bump.sh major     # 0.8.0 → 1.0.0
```

Does not commit or create a tag (configured in `.bumpversion.toml`).

## Building and Publishing

Build the package locally and check it:

```bash
scripts/build.sh
```

Upload to test PyPI or production PyPI:

```bash
scripts/build.sh test     # upload to test.pypi.org
scripts/build.sh pypi     # upload to pypi.org
```

Requires `twine` (included in `requirements_dev.txt`).

## Project Layout

```
mydot/
├── mydot/              # source package
│   ├── __init__.py     # version + public API
│   ├── __main__.py     # CLI entry point (argparse)
│   ├── actions.py      # action classes (edit, grep, history, fzf, etc.)
│   ├── repository.py   # Repository class (git queries, file lists)
│   ├── editor.py       # editor discovery + open protocol
│   ├── clip.py         # clipboard discovery + copy protocol
│   ├── console.py      # rich console + theme
│   ├── logging.py      # logging config
│   └── exceptions.py   # custom exceptions
├── tests/              # pytest suite
│   ├── conftest.py     # shared fixtures (fake_repo, clean_repo, submodule_repo)
│   └── test_*.py       # test modules
├── scripts/            # development scripts
│   ├── venv-create.sh  # create .venv
│   ├── test.sh         # run tests
│   ├── test-watch.sh   # continuous testing
│   ├── bump.sh         # version bumping
│   └── build.sh        # build + publish
├── docs/               # documentation
├── setup.py            # package metadata
├── requirements.txt    # runtime deps
└── requirements_dev.txt # dev deps
```

## Typical Workflow

```bash
# 1. Set up environment
scripts/venv-create.sh && source .venv/bin/activate

# 2. Write code + tests
scripts/test-watch.sh       # in a separate terminal

# 3. When ready to release
scripts/test.sh             # final check
scripts/bump.sh patch       # edit version files (no commit, no tag)
git commit -am "vX.Y.Z"     # commit the bump
git push                    # push the branch (no tag yet)
# merge request the branch onto master (squash)
git checkout master && git pull
git tag vX.Y.Z              # tag the squash-merge commit on master
git push --tags

# 4. Publish
scripts/build.sh test       # verify on test.pypi.org
scripts/build.sh pypi       # publish to pypi.org
```
