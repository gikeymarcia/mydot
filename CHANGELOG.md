All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).


## [Unreleased]

### Changed

- CLI short flag for `--list` changed to `-l` from `-ls`

## [0.5.0 ] - 2021-09-30

### Added

- `--clip` option to throw put file paths into the clipboard

## [0.4.0 ] - 2021-09-27

### Added

- `--discard` option to throw away changes in the work-tree

## [0.3.8] - 2021-09-25

### Added

- This changelog.

### Changed

- Changed the logic of how I parse `git status -s --porecelain` renamed files

### Fixed

- A bug caused when a file was both renamed and modified. These files were 
incorrectly parsed by various selectors. I fixed the bug and added regression 
tests to ensure future functionality.

