"""Smoke test suite to verify baseline package imports and structure."""

import apricot
import apricot.agent
import apricot.config
import apricot.github
import apricot.models
import apricot.repository
import apricot.tools
import apricot.utils


def test_import_apricot() -> None:
    """Verify that apricot package can be imported and exports a version."""
    assert apricot.__version__ == "0.1.0"


def test_subpackages_importable() -> None:
    """Verify that all foundational subpackages are importable."""
    assert apricot.agent is not None
    assert apricot.tools is not None
    assert apricot.repository is not None
    assert apricot.models is not None
    assert apricot.github is not None
    assert apricot.config is not None
    assert apricot.utils is not None
