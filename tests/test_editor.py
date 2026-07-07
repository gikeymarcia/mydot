from unittest.mock import patch

from mydot.editor import (
    MissingEditor,
    Nano,
    Neovim,
    UserDefinedEditor,
    Vim,
    find_editor,
)


def _mock_which(available):
    """Return a shutil.which mock that knows about `available` binaries."""
    def which(name):
        return f"/usr/bin/{name}" if name in available else None
    return which


class TestFindEditorWithEnv:
    """Tests for find_editor() when $EDITOR is set."""

    def test_editor_env_nvim(self, monkeypatch):
        monkeypatch.setenv("EDITOR", "nvim")
        result = find_editor()
        assert isinstance(result, Neovim)

    def test_editor_env_vim(self, monkeypatch):
        monkeypatch.setenv("EDITOR", "vim")
        result = find_editor()
        assert isinstance(result, Vim)

    def test_editor_env_nano(self, monkeypatch):
        monkeypatch.setenv("EDITOR", "nano")
        result = find_editor()
        assert isinstance(result, Nano)

    def test_editor_env_custom(self, monkeypatch):
        monkeypatch.setenv("EDITOR", "emacs")
        result = find_editor()
        assert isinstance(result, UserDefinedEditor)
        assert result.program == "emacs"

    def test_editor_env_nvim_full_path(self, monkeypatch):
        # macOS/Homebrew commonly sets EDITOR to an absolute path; the basename
        # should still resolve to the built-in class so search is supported.
        monkeypatch.setenv("EDITOR", "/opt/homebrew/bin/nvim")
        result = find_editor()
        assert isinstance(result, Neovim)

    def test_editor_env_vim_full_path(self, monkeypatch):
        monkeypatch.setenv("EDITOR", "/usr/bin/vim")
        result = find_editor()
        assert isinstance(result, Vim)

    def test_editor_env_custom_full_path(self, monkeypatch):
        # An absolute path to an unknown editor keeps the full path as the program.
        monkeypatch.setenv("EDITOR", "/usr/local/bin/emacs")
        result = find_editor()
        assert isinstance(result, UserDefinedEditor)
        assert result.program == "/usr/local/bin/emacs"


class TestFindEditorFallback:
    """Tests for find_editor() falling back through $PATH search."""

    def test_finds_nvim_first(self, monkeypatch):
        monkeypatch.delenv("EDITOR", raising=False)
        with patch("mydot.editor.shutil.which", _mock_which(["nvim", "vim", "nano"])):
            result = find_editor()
        assert isinstance(result, Neovim)

    def test_finds_vim_when_no_nvim(self, monkeypatch):
        monkeypatch.delenv("EDITOR", raising=False)
        with patch("mydot.editor.shutil.which", _mock_which(["vim", "nano"])):
            result = find_editor()
        assert isinstance(result, Vim)

    def test_finds_nano_when_no_vim(self, monkeypatch):
        monkeypatch.delenv("EDITOR", raising=False)
        with patch("mydot.editor.shutil.which", _mock_which(["nano"])):
            result = find_editor()
        assert isinstance(result, Nano)

    def test_finds_kate_as_user_defined(self, monkeypatch):
        monkeypatch.delenv("EDITOR", raising=False)
        with patch("mydot.editor.shutil.which", _mock_which(["kate"])):
            result = find_editor()
        assert isinstance(result, UserDefinedEditor)
        assert result.program == "kate"

    def test_finds_gedit_as_user_defined(self, monkeypatch):
        monkeypatch.delenv("EDITOR", raising=False)
        with patch("mydot.editor.shutil.which", _mock_which(["gedit"])):
            result = find_editor()
        assert isinstance(result, UserDefinedEditor)
        assert result.program == "gedit"

    def test_returns_missing_when_nothing_found(self, monkeypatch):
        monkeypatch.delenv("EDITOR", raising=False)
        with patch("mydot.editor.shutil.which", _mock_which([])):
            result = find_editor()
        assert isinstance(result, MissingEditor)
