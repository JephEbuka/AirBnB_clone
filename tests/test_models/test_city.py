#!/usr/bin/python3
"""Verify the City model's defaults and inherited behavior."""

from models.city import City
from tests.helpers import StorageTestCase
from tests.model_cases import ModelContractMixin


class TestCity(ModelContractMixin, StorageTestCase):
    """Exercise City independently and through shared file storage."""

    model_class = City
    defaults = {"state_id": "", "name": ""}
