from unittest.mock import patch

from mydot.clip import NoApp, Pbcopy, Xclip, Xsel, find_clipper


def _mock_which(available):
    """Return a shutil.which mock that knows about `available` binaries."""
    def which(name):
        return f"/usr/bin/{name}" if name in available else None
    return which


def test_find_clipper_xclip():
    with patch("mydot.clip.shutil.which", _mock_which(["xclip", "xsel", "pbcopy"])):
        result = find_clipper()
    assert isinstance(result, Xclip)


def test_find_clipper_xsel_when_no_xclip():
    with patch("mydot.clip.shutil.which", _mock_which(["xsel", "pbcopy"])):
        result = find_clipper()
    assert isinstance(result, Xsel)


def test_find_clipper_pbcopy_when_no_xsel():
    with patch("mydot.clip.shutil.which", _mock_which(["pbcopy"])):
        result = find_clipper()
    assert isinstance(result, Pbcopy)


def test_find_clipper_noapp_fallback():
    with patch("mydot.clip.shutil.which", _mock_which([])):
        result = find_clipper()
    assert isinstance(result, NoApp)


def test_has_app_true():
    clip = Xclip()
    with patch("mydot.clip.shutil.which", _mock_which(["xclip"])):
        assert clip.has_app() is True


def test_has_app_false():
    clip = Xclip()
    with patch("mydot.clip.shutil.which", _mock_which([])):
        assert clip.has_app() is False
