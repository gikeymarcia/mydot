# Project Architecture

## Stage 1

To begin I'm pulling all of the actions out of the `Repository` class.

- My Dot Actions
    - [X] Clip
    - [X] Git
    - [X] Add
    - [ ] Export
    - [ ] Edit
    - [ ] Run
    - [ ] Grep
    - [ ] Restore
    - [ ] Discard
    - [ ] Status
    - [ ] List2



## Stage 2


- [ ] Make a new Dotfile() class that is a file_path + powers
    - The idea is to use `Repository` to query subsets of the files under
      version control and make a standardized `Dotfile` object which each
      property of `Repository` would return an Iterable of.

- Repository(bare_repo, work_tree)
    - [ ] Only Used to query the `Repository` and each call should return an
      Iterable of `Dotfile`s.
        - [ ] **list_all**
        - [ ] **deleted_staged**: Return all files staged for deletion
        - [ ] **modified_unstaged**
        - [ ] **modified_staged**
        - [ ] **restorables**: all files affected by `git restore --staged`.
        - [ ] **work_tree**
        - [ ] **bare_repo**
        - [ ] **short_status**
        - [ ] **tracked**
        - [ ] **adds_staged**: list of newly added files to the staging area
        - [ ] **oldnames**: previous name of files renamed in staging area.
        - [ ] **renames**: Files renamed

## On the table - not on the roadmap (yet)

- Filter = Callable[..., Iterable[Dotfile]]
    - `__init__(self, source: Repository)`
    - NoBinaries(Repository)
    - Relative_to(Repository, Repository.work_tree)
    - Executable(Repository)


- Make previewers use solid design. Think about the [factory design
  pattern][factory].

    ```python
    class Previewer(Protocol)

        def view(filepath: Path) -> str:
            pass
    ```


[factory]: <https://www.geeksforgeeks.org/factory-method-python-design-patterns/>
"Factory Method - Python Design Patterns @ GeeksforGeeks"
