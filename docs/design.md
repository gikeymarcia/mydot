# Project Architecture

As-is the `Dotfiles` class is doing too much. It needs to be split up into
smaller units with more clear responsiblities.

Objects:

- Repository(bare_repo, work_tree)
    - Make a new Dotfile() class that is a file_path + powers
    - Should only be used to query types of files in the repo
    - properties -> Iterable[Dotfile]
        - [X] **list_all**
        - [X] **deleted_staged**: Return all files staged for deletion
        - [X] **modified_unstaged**
        - [X] **modified_staged**
        - [X] **restorables**: all files affected by `git restore --staged`.
        - [X] **work_tree**
        - [X] **bare_repo**
        - [X] **short_status**
        - [X] **tracked**
        - [X] **adds_staged**: list of newly added files to the staging area
        - [X] **oldnames**: previous name of files renamed in staging area.
        - [X] **renames**: Files renamed

- Filter = Callable[..., Iterable[Dotfile]]
    - `__init__(self, source: Repository)`
    - NoBinaries(Repository)
    - Relative_to(Repository, Repository.work_tree)
    - Executable(Repository)


- My Dot Actions
    - [X] Clip
    - [X] Git
    - [ ] Edit
    - [ ] Add
    - [ ] Export
    - [ ] Run
    - [ ] Grep
    - [ ] Restore
    - [ ] Discard
    - [ ] Status
    - [ ] List2

- Make previewers use solid design. Think about the [factory design
  pattern][factory].

    ```python
    class Previewer(Protocol)

        def view(filepath: Path) -> str:
            pass
    ```


[factory]: <https://www.geeksforgeeks.org/factory-method-python-design-patterns/>
"Factory Method - Python Design Patterns @ GeeksforGeeks"
