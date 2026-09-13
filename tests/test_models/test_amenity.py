#!/usr/bin/python3
"""Verify the Amenity model's defaults and inherited behavior."""

from models.amenity import Amenity
from tests.helpers import StorageTestCase
from tests.model_cases import ModelContractMixin


class TestAmenity(ModelContractMixin, StorageTestCase):
    """Exercise Amenity independently and through shared file storage."""

    model_class = Amenity
    defaults = {"name": ""}
