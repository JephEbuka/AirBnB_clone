#!/usr/bin/python3
"""Reusable behavior checks for each concrete AirBnB model class."""

from datetime import datetime, timedelta
import json
from unittest.mock import patch
from uuid import UUID

from models import storage
from models.base_model import BaseModel


class ModelContractMixin:
    """Check a concrete model against inherited and declared behavior."""

    def test_inheritance_identity_and_timestamps(self):
        """Each concrete model has BaseModel identity and datetime fields."""
        instance = self.model_class()
        self.assertIsInstance(instance, BaseModel)
        self.assertIsInstance(instance.id, str)
        self.assertEqual(UUID(instance.id).version, 4)
        self.assertNotEqual(instance.id, self.model_class().id)
        self.assertIsInstance(instance.created_at, datetime)
        self.assertIsInstance(instance.updated_at, datetime)

    def test_default_class_attributes(self):
        """Required default values and types are public class attributes."""
        instance = self.model_class()
        for name, expected in self.defaults.items():
            with self.subTest(attribute=name):
                self.assertIn(name, self.model_class.__dict__)
                self.assertNotIn(name, instance.__dict__)
                self.assertEqual(getattr(instance, name), expected)
                self.assertIs(type(getattr(instance, name)), type(expected))

    def test_new_instance_is_registered_under_concrete_class(self):
        """The storage key uses the concrete class and the generated ID."""
        instance = self.model_class()
        key = "{}.{}".format(self.model_class.__name__, instance.id)
        self.assertIs(storage.all()[key], instance)

    def test_to_dict_serializes_only_instance_attributes(self):
        """Unset class defaults are excluded from instance serialization."""
        instance = self.model_class()
        self.assertEqual(set(instance.to_dict()),
                         {"id", "created_at", "updated_at", "__class__"})
        instance.custom_text = "Example value"
        result = instance.to_dict()
        self.assertEqual(result["__class__"], self.model_class.__name__)
        self.assertEqual(result["custom_text"], "Example value")
        self.assertEqual(result["created_at"], instance.created_at.isoformat())
        self.assertEqual(json.loads(json.dumps(result)), result)
        self.assertNotIn("__class__", instance.__dict__)

    def test_string_representation_uses_concrete_class(self):
        """The string representation identifies the concrete model."""
        instance = self.model_class()
        expected = "[{}] ({}) {}".format(
            self.model_class.__name__, instance.id, instance.__dict__)
        self.assertEqual(str(instance), expected)

    def test_reconstruction_preserves_data_and_registration(self):
        """Dictionary reconstruction neither duplicates nor registers."""
        instance = self.model_class()
        instance.custom_text = "Restored value"
        data = instance.to_dict()
        restored = self.model_class(**data)
        self.assertIsNot(restored, instance)
        self.assertIs(type(restored), self.model_class)
        self.assertEqual(restored.__dict__, instance.__dict__)
        self.assertEqual(data, instance.to_dict())
        self.assertEqual(len(storage.all()), 1)
        self.assertIs(next(iter(storage.all().values())), instance)

    def test_save_and_reload_preserve_concrete_model(self):
        """Storage recreates the correct concrete class with saved values."""
        instance = self.model_class()
        instance.custom_text = "Saved model"
        instance.custom_number = 89
        instance.save()
        expected = instance.to_dict()
        key = "{}.{}".format(self.model_class.__name__, instance.id)
        storage.all().clear()
        storage.reload()
        restored = storage.all()[key]
        self.assertIs(type(restored), self.model_class)
        self.assertEqual(restored.to_dict(), expected)
        self.assertIsInstance(restored.created_at, datetime)
        self.assertIsInstance(restored.updated_at, datetime)

    def test_save_refreshes_updated_at(self):
        """An inherited save refreshes updated_at and retains created_at."""
        instance = self.model_class()
        created = instance.created_at
        later = instance.updated_at + timedelta(days=1)
        with patch("models.base_model.datetime") as clock:
            clock.now.return_value = later
            instance.save()
        self.assertEqual(instance.updated_at, later)
        self.assertEqual(instance.created_at, created)

    def test_instance_changes_do_not_change_class_defaults(self):
        """Assigning a field affects that object, not a later new object."""
        instance = self.model_class()
        for name, default in self.defaults.items():
            if isinstance(default, str):
                setattr(instance, name, "Changed")
            elif isinstance(default, list):
                setattr(instance, name, ["amenity-id"])
            else:
                setattr(instance, name, type(default)(1))
        later = self.model_class()
        for name, expected in self.defaults.items():
            self.assertEqual(getattr(later, name), expected)
            self.assertEqual(getattr(self.model_class, name), expected)
