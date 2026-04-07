from conftest import appears_in


def test_freshen_clears_short_status(fake_repo):
    dotfiles = fake_repo["df"]
    # Access to populate cache
    first = dotfiles.short_status
    assert "short_status" in dotfiles.__dict__

    dotfiles.freshen()
    assert "short_status" not in dotfiles.__dict__

    # Next access should recompute and match
    second = dotfiles.short_status
    assert first == second


def test_freshen_clears_list_all(fake_repo):
    dotfiles = fake_repo["df"]
    first = dotfiles.list_all
    assert "list_all" in dotfiles.__dict__

    dotfiles.freshen()
    assert "list_all" not in dotfiles.__dict__

    second = dotfiles.list_all
    assert first == second


def test_freshen_clears_restorables(fake_repo):
    dotfiles = fake_repo["df"]
    first = dotfiles.restorables
    assert "restorables" in dotfiles.__dict__

    dotfiles.freshen()
    assert "restorables" not in dotfiles.__dict__

    second = dotfiles.restorables
    assert first == second


def test_freshen_clears_executables(fake_repo):
    dotfiles = fake_repo["df"]
    first = dotfiles.executables
    assert "executables" in dotfiles.__dict__

    dotfiles.freshen()
    assert "executables" not in dotfiles.__dict__

    second = dotfiles.executables
    assert first == second


def test_freshen_reflects_new_changes(fake_repo):
    """After staging a change and calling freshen(), selectors update."""
    dotfiles = fake_repo["df"]
    git = fake_repo["git"]

    unstaged_before = dotfiles.modified_unstaged
    assert len(unstaged_before) > 0

    # Stage all unstaged modifications
    for f in unstaged_before:
        git(["add", "--", f])
    dotfiles.freshen()

    assert dotfiles.modified_unstaged == []


def test_clean_repo_list_all(clean_repo):
    """A clean repo's list_all should equal its tracked files."""
    dotfiles = clean_repo["df"]
    assert dotfiles.list_all == sorted(dotfiles.tracked)
    assert dotfiles.modified_unstaged == []
    assert dotfiles.modified_staged == []
    assert dotfiles.adds_staged == []
    assert dotfiles.deleted_staged == []
    assert dotfiles.restorables == []
