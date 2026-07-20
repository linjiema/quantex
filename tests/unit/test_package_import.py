"""Smoke tests for the new package boundary."""

from importlib import import_module

import pytest


@pytest.mark.parametrize(
    "module_name",
    [
        "quantex",
        "quantex.application",
        "quantex.core",
        "quantex.gui",
        "quantex.hardware",
        "quantex.interfaces",
        "quantex.logic",
        "quantex.services",
    ],
)
def test_package_module_imports(module_name: str) -> None:
    assert import_module(module_name) is not None
