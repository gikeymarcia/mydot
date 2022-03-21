# Project Architecture

As-is the `Dotfiles` class is doing too much. It needs to be split up into
smaller units with more clear responsiblities.

Objects:

- Repository(bare_repo, work_tree)
    - Make a new Dotfile() class that is a file_path + powers
    - Should only be used to query types of files in the repo
    - properties -> Iterable[Dotfile]
        - **list_all**
        - **deleted_staged**: Return all files staged for deletion
        - **modified_unstaged**
        - **modified_staged**
        - **modified_unstaged**
        - **restorables**: all files affected by `git restore --staged`.
        - **work_tree**
        - **bare_repo**
        - **short_status**
        - **tracked**
        - **adds_staged**: list of newly added files to the staging area
        - **oldnames**: previous name of files renamed in staging area.
        - **renames**: Files renamed

- Filter = Callable[..., Iterable[Dotfile]]
    - `__init__(self, source: Repository)`
    - NoBinaries(Repository)
    - Relative_to(Repository, Repository.work_tree)
    - Executable(Repository)


- My Dot Actions
    - Edit
    - Clip
    - Add
    - Export
    - Git
    - Run
    - Grep
    - Restore
    - Discard
    - Status
    - List2

- Make previewers use solid design. Think about the [factory design
  pattern][factory].

    ```python
    class Previewer(Protocol)

        def view(filepath: Path) -> str:
            pass
    ```


[factory]: <https://www.geeksforgeeks.org/factory-method-python-design-patterns/>
"Factory Method - Python Design Patterns @ GeeksforGeeks"
