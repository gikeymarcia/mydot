#!/usr/bin/env python3
# Mikey Garcia, @gikeymarcia
# https://github.com/gikeymarcia/mydot

from conftest import appears_in


def test_tracked(fake_repo):
    dotfiles = fake_repo["df"]
    tracked = appears_in(fake_repo, "tracked")
    assert dotfiles.tracked == tracked


def test_list_all(fake_repo):
    dotfiles = fake_repo["df"]
    fake_repo["status"]()
    list_all = appears_in(fake_repo, "list")
    assert dotfiles.list_all == list_all


def test_oldnames(fake_repo):
    dotfiles = fake_repo["df"]
    dotfiles.freshen()
    fake_repo["status"]()
    old = appears_in(fake_repo, "oldname")
    assert dotfiles.oldnames == old


def test_renames(fake_repo):
    dotfiles = fake_repo["df"]
    dotfiles.freshen()
    fake_repo["status"]()
    renames = appears_in(fake_repo, "rename")
    assert dotfiles.renames == renames


def test_adds_staged(fake_repo):
    dotfiles = fake_repo["df"]
    adds = appears_in(fake_repo, "adds_staged")
    assert dotfiles.adds_staged == adds
    for file in adds:
        fake_repo["git"](["restore", "--staged", file])
    dotfiles.freshen()
    assert dotfiles.adds_staged == []


def test_deleted_staged(fake_repo):
    dotfiles = fake_repo["df"]
    deleted = appears_in(fake_repo, "deleted")
    assert dotfiles.deleted_staged == deleted
    for file in deleted:
        fake_repo["git"](["restore", "--staged", "--", file])
    dotfiles.freshen()
    assert dotfiles.deleted_staged == []


def test_modfied_staged(fake_repo):
    dotfiles = fake_repo["df"]
    modified_staged = appears_in(fake_repo, "modified_staged")
    assert dotfiles.modified_staged == modified_staged
    for file in modified_staged:
        fake_repo["git"](["restore", "--staged", "--", file])
    dotfiles.freshen()
    assert dotfiles.modified_staged == []


def test_modfied_UNstaged(fake_repo):
    dotfiles = fake_repo["df"]
    fake_repo["status"]()
    modified_unstaged = appears_in(fake_repo, "modified_unstaged")
    assert dotfiles.modified_unstaged == sorted(modified_unstaged)
    for file in modified_unstaged:
        fake_repo["git"](["add", "--", file])
    dotfiles.freshen()
    assert dotfiles.modified_unstaged == []


def test_restorables(fake_repo):
    dotfiles = fake_repo["df"]
    fake_repo["status"]()
    restorable = appears_in(fake_repo, "restore")
    assert dotfiles.restorables == restorable


# vim: foldlevel=1:
