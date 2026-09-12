#!/usr/bin/python3
"""Verify identity, timestamps, dictionaries and model save behavior."""

from datetime import datetime, timedelta
import json
import os
from unittest.mock import patch
from uuid import UUID

from models import storage
from models.base_model import BaseModel
from tests.helpers import StorageTestCase


class TestBaseModel(StorageTestCase):
    """Exercise the BaseModel contract in tasks 3–5."""

    def test_id_is_uuid4_string(self):
        """A fresh model has a string UUID version 4."""
        instance = BaseModel()
        self.assertIsInstance(instance.id, str)
        self.assertEqual(UUID(instance.id).version, 4)

    def test_ids_are_unique(self):
        """Independent objects receive independent identities."""
        identifiers = {BaseModel().id for _ in range(100)}
        self.assertEqual(len(identifiers), 100)

    def test_new_timestamps_are_current_datetimes(self):
        """Both timestamp attributes fall within the construction window."""
        before = datetime.now()
        instance = BaseModel()
        after = datetime.now()
        for value in (instance.created_at, instance.updated_at):
            self.assertIsInstance(value, datetime)
            self.assertLessEqual(before, value)
            self.assertLessEqual(value, after)

    def test_new_object_registers_itself(self):
        """The shared registry contains the exact newly constructed object."""
        instance = BaseModel()
        self.assertIs(storage.all()["BaseModel." + instance.id], instance)

    def test_construction_does_not_save_to_disk(self):
        """Registration alone does not create a JSON file."""
        BaseModel()
        self.assertFalse(os.path.exists(self.path))

    def test_positional_arguments_are_ignored(self):
        """Positional arguments do not override generated attributes."""
        instance = BaseModel("ignored", 42, None)
        self.assertEqual(set(instance.__dict__),
                         {"id", "created_at", "updated_at"})

    def test_empty_kwargs_create_new_object(self):
        """An empty dictionary uses the fresh-instance path."""
        instance = BaseModel(**{})
        self.assertIn("BaseModel." + instance.id, storage.all())

    def test_string_representation(self):
        """String conversion contains the class, ID and attributes."""
        instance = BaseModel()
        instance.name = "Example"
        expected = "[BaseModel] ({}) {}".format(
            instance.id, instance.__dict__)
        self.assertEqual(str(instance), expected)

    def test_to_dict_contains_all_instance_attributes(self):
        """Custom attributes and class metadata appear in the result."""
        instance = BaseModel()
        instance.name = "My First Model"
        instance.my_number = 89
        result = instance.to_dict()
        self.assertEqual(set(result), set(instance.__dict__) | {"__class__"})
        self.assertEqual(result["name"], instance.name)
        self.assertEqual(result["my_number"], 89)
        self.assertEqual(result["__class__"], "BaseModel")

    def test_to_dict_converts_timestamps_to_iso_strings(self):
        """Both datetime attributes become their ISO string values."""
        instance = BaseModel()
        result = instance.to_dict()
        for name in ("created_at", "updated_at"):
            self.assertEqual(result[name], getattr(instance, name).isoformat())
            self.assertIsInstance(result[name], str)

    def test_to_dict_does_not_mutate_model(self):
        """Serialization leaves instance attributes and types intact."""
        instance = BaseModel()
        original = instance.__dict__.copy()
        result = instance.to_dict()
        result["id"] = "changed"
        self.assertEqual(instance.__dict__, original)
        self.assertNotIn("__class__", instance.__dict__)
        self.assertIsNot(instance.to_dict(), instance.to_dict())

    def test_dictionary_can_be_encoded_as_json(self):
        """The standard JSON encoder accepts the model dictionary."""
        result = BaseModel().to_dict()
        self.assertEqual(json.loads(json.dumps(result)), result)

    def test_reconstruction_round_trip(self):
        """A reconstructed object has equal data and different identity."""
        instance = BaseModel()
        instance.name = "Restored"
        instance.my_number = 89
        restored = BaseModel(**instance.to_dict())
        self.assertIsNot(restored, instance)
        self.assertEqual(restored.__dict__, instance.__dict__)

    def test_reconstruction_does_not_register_or_replace(self):
        """Dictionary construction does not replace a registered object."""
        instance = BaseModel()
        BaseModel(**instance.to_dict())
        self.assertEqual(len(storage.all()), 1)
        self.assertIs(storage.all()["BaseModel." + instance.id], instance)

    def test_reconstruction_ignores_class_metadata(self):
        """The metadata key never becomes an instance attribute."""
        data = BaseModel().to_dict()
        data["__class__"] = "AnotherClass"
        instance = BaseModel(**data)
        self.assertIs(type(instance), BaseModel)
        self.assertNotIn("__class__", instance.__dict__)

    def test_reconstruction_does_not_mutate_input(self):
        """Input timestamp strings and other values remain untouched."""
        data = BaseModel().to_dict()
        original = data.copy()
        BaseModel(**data)
        self.assertEqual(data, original)

    def test_reconstruction_without_fractional_seconds(self):
        """ISO strings produced at an exact second can be reconstructed."""
        data = BaseModel().to_dict()
        data["created_at"] = "2026-09-07T12:00:00"
        data["updated_at"] = "2026-09-07T12:00:01"
        instance = BaseModel(**data)
        self.assertEqual(instance.created_at, datetime(2026, 9, 7, 12))
        self.assertEqual(instance.updated_at,
                         datetime(2026, 9, 7, 12, 0, 1))

    def test_partial_kwargs_are_preserved_without_new_defaults(self):
        """Nonempty kwargs restore only the supplied attributes."""
        instance = BaseModel(name="Only supplied attribute", number=7)
        self.assertEqual(instance.__dict__,
                         {"name": "Only supplied attribute", "number": 7})
        self.assertEqual(storage.all(), {})

    def test_invalid_timestamp_raises_value_error(self):
        """Malformed saved timestamp strings are rejected."""
        with self.assertRaises(ValueError):
            BaseModel(created_at="not-a-date")

    def test_save_updates_timestamp_and_preserves_creation(self):
        """Saving updates the modification time using the current clock."""
        instance = BaseModel()
        created = instance.created_at
        later = instance.updated_at + timedelta(days=1)
        with patch("models.base_model.datetime") as clock:
            clock.now.return_value = later
            instance.save()
        self.assertEqual(instance.updated_at, later)
        self.assertEqual(instance.created_at, created)

    def test_save_persists_custom_attributes(self):
        """Saving writes the object's serialized attributes to JSON."""
        instance = BaseModel()
        instance.name = "Saved value"
        self.assertIsNone(instance.save())
        with open(self.path, encoding="utf-8") as stream:
            saved = json.load(stream)
        self.assertEqual(saved["BaseModel." + instance.id], instance.to_dict())

    def test_save_calls_shared_storage(self):
        """The save method delegates persistence to shared storage."""
        instance = BaseModel()
        with patch.object(storage, "save") as persist:
            instance.save()
        persist.assert_called_once_with()
