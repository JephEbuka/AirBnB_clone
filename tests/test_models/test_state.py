#!/usr/bin/python3
"""Verify the State model's defaults and inherited behavior."""

from models.state import State
from tests.helpers import StorageTestCase
from tests.model_cases import ModelContractMixin


class TestState(ModelContractMixin, StorageTestCase):
    """Exercise State independently and through shared file storage."""

    model_class = State
    defaults = {"name": ""}
