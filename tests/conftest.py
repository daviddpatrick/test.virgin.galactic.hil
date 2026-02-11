import pytest


def pytest_addoption(parser):
    parser.addoption("--test_env", default=None, help="Test Automation Environment (US etc...)")
