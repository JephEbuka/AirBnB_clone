#!/usr/bin/python3
"""Verify the Place model's fields and inherited behavior."""

from models import storage
from models.place import Place
from tests.helpers import StorageTestCase
from tests.model_cases import ModelContractMixin


class TestPlace(ModelContractMixin, StorageTestCase):
    """Exercise Place independently and through shared file storage."""

    model_class = Place
    defaults = {
        "city_id": "", "user_id": "", "name": "", "description": "",
        "number_rooms": 0, "number_bathrooms": 0, "max_guest": 0,
        "price_by_night": 0, "latitude": 0.0, "longitude": 0.0,
        "amenity_ids": [],
    }

    def test_amenity_ids_assignment_round_trip(self):
        """An explicitly assigned amenity list survives saving and reload."""
        instance = Place()
        instance.amenity_ids = ["wifi-id", "parking-id"]
        instance.save()
        storage.all().clear()
        storage.reload()
        restored = storage.all()["Place." + instance.id]
        self.assertEqual(restored.amenity_ids, ["wifi-id", "parking-id"])
        self.assertEqual(Place.amenity_ids, [])
