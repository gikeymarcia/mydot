from pathlib import Path
from unittest.mock import patch

import pytest

from mydot.exceptions import WorktreeMissing
from mydot.repository import Repository


class TestResolveWorkTree:
    def test_none_defaults_to_home(self):
        result = Repository._resolve_work_tree_location(None)
        assert result == Path.home()

    def test_valid_dir_as_string(self, tmp_path):
        result = Repository._resolve_work_tree_location(str(tmp_path))
        assert result == tmp_path

    def test_valid_dir_as_path(self, tmp_path):
        result = Repository._resolve_work_tree_location(tmp_path)
        assert result == tmp_path

    def test_nonexistent_dir_raises(self, tmp_path):
        bogus = tmp_path / "does_not_exist"
        with pytest.raises(WorktreeMissing):
            Repository._resolve_work_tree_location(bogus)

    def test_nonexistent_dir_as_string_raises(self, tmp_path):
        bogus = str(tmp_path / "nope")
        with pytest.raises(WorktreeMissing):
            Repository._resolve_work_tree_location(bogus)


class TestPreviewApp:
    def _mock_which(self, available):
        def which(name):
            return f"/usr/bin/{name}" if name in available else None
        return which

    def test_bat_first(self, clean_repo):
        dotfiles = clean_repo["df"]
        dotfiles.__dict__.pop("preview_app", None)
        with patch("mydot.repository.shutil.which", self._mock_which(["bat", "batcat"])):
            assert dotfiles.preview_app == "bat --color=always"

    def test_batcat_when_no_bat(self, clean_repo):
        dotfiles = clean_repo["df"]
        dotfiles.__dict__.pop("preview_app", None)
        with patch("mydot.repository.shutil.which", self._mock_which(["batcat"])):
            assert dotfiles.preview_app == "batcat --color=always"

    def test_highlight_when_no_bat(self, clean_repo):
        dotfiles = clean_repo["df"]
        dotfiles.__dict__.pop("preview_app", None)
        with patch("mydot.repository.shutil.which", self._mock_which(["highlight"])):
            assert dotfiles.preview_app == "highlight -O ansi"

    def test_cat_fallback(self, clean_repo):
        dotfiles = clean_repo["df"]
        dotfiles.__dict__.pop("preview_app", None)
        with patch("mydot.repository.shutil.which", self._mock_which([])):
            assert dotfiles.preview_app == "cat"


class TestExecutables:
    def test_executables_detected(self, clean_repo):
        """Files with the executable bit should appear in executables."""
        dotfiles = clean_repo["df"]
        worktree = clean_repo["worktree"]

        script = worktree / "fileA"
        script.chmod(0o755)
        dotfiles.freshen()

        assert "fileA" in dotfiles.executables

    def test_non_executable_excluded(self, clean_repo):
        dotfiles = clean_repo["df"]
        worktree = clean_repo["worktree"]

        for f in worktree.iterdir():
            if f.is_file():
                f.chmod(0o644)
        dotfiles.freshen()

        assert dotfiles.executables == []
