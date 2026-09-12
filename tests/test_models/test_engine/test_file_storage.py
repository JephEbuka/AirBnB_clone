#!/usr/bin/python3
"""Verify storage registration, disk persistence and restoration."""

import json
import os
import unittest
from unittest.mock import patch

import models
from models.base_model import BaseModel
from models.engine.file_storage import FileStorage
from tests.helpers import StorageTestCase


class TestFileStorageClassAttributes(unittest.TestCase):
    """Verify the two private class attributes named in the checker."""

    def test_file_path_is_private_class_string(self):
        """The default file path exists on the class and equals file.json."""
        self.assertIn("_FileStorage__file_path", FileStorage.__dict__)
        self.assertIs(type(FileStorage._FileStorage__file_path), str)
        self.assertEqual(FileStorage._FileStorage__file_path, "file.json")
        self.assertFalse(hasattr(FileStorage(), "__file_path"))

    def test_objects_is_private_class_dictionary(self):
        """The class declares a shared dictionary accessible through all."""
        self.assertIn("_FileStorage__objects", FileStorage.__dict__)
        self.assertIs(type(FileStorage._FileStorage__objects), dict)
        self.assertIs(FileStorage().all(), FileStorage._FileStorage__objects)
        self.assertFalse(hasattr(FileStorage(), "__objects"))


class TestFileStorage(StorageTestCase):
    """Exercise the file-storage requirements from task 5."""

    def test_models_exports_storage_instance(self):
        """The models package exposes shared FileStorage."""
        self.assertIsInstance(models.storage, FileStorage)

    def test_all_returns_live_dictionary(self):
        """The returned registry is the shared mutable dictionary."""
        engine = FileStorage()
        registry = engine.all()
        self.assertIsInstance(registry, dict)
        self.assertIs(registry, engine.all())
        self.assertEqual(registry, {})
        BaseModel()
        self.assertEqual(len(registry), 1)

    def test_storage_instances_share_objects(self):
        """Objects are held in the required class-level dictionary."""
        first, second = FileStorage(), FileStorage()
        self.assertIs(first.all(), second.all())

    def test_new_uses_class_and_id_key(self):
        """Explicit registration stores the supplied object under its key."""
        instance = BaseModel()
        models.storage.all().clear()
        self.assertIsNone(models.storage.new(instance))
        self.assertEqual(models.storage.all(),
                         {"BaseModel." + instance.id: instance})

    def test_new_replaces_same_key(self):
        """Explicit registration of a reconstructed object replaces its key."""
        original = BaseModel()
        replacement = BaseModel(**original.to_dict())
        models.storage.new(replacement)
        self.assertIs(models.storage.all()["BaseModel." + original.id],
                      replacement)
        self.assertEqual(len(models.storage.all()), 1)

    def test_save_empty_dictionary(self):
        """Saving an empty registry produces an empty JSON object."""
        self.assertIsNone(models.storage.save())
        with open(self.path, encoding="utf-8") as stream:
            self.assertEqual(json.load(stream), {})

    def test_save_multiple_models(self):
        """Every registered object is represented in the JSON file."""
        first, second = BaseModel(), BaseModel()
        first.name = "First"
        second.number = 89
        models.storage.save()
        with open(self.path, encoding="utf-8") as stream:
            saved = json.load(stream)
        self.assertEqual(saved, {"BaseModel." + first.id: first.to_dict(),
                                 "BaseModel." + second.id: second.to_dict()})

    def test_save_overwrites_previous_snapshot(self):
        """A removed object disappears from the next disk snapshot."""
        instance = BaseModel()
        instance.save()
        models.storage.all().clear()
        models.storage.save()
        with open(self.path, encoding="utf-8") as stream:
            self.assertEqual(json.load(stream), {})

    def test_reload_missing_file_is_noop(self):
        """A missing JSON file does not raise or clear in-memory objects."""
        instance = BaseModel()
        self.assertFalse(os.path.exists(self.path))
        self.assertIsNone(models.storage.reload())
        self.assertIs(models.storage.all()["BaseModel." + instance.id],
                      instance)

    def test_reload_empty_file_dictionary(self):
        """An empty valid snapshot produces no new objects."""
        with open(self.path, "w", encoding="utf-8") as stream:
            json.dump({}, stream)
        models.storage.reload()
        self.assertEqual(models.storage.all(), {})

    def test_reload_reconstructs_objects_and_timestamps(self):
        """Saved objects return with the same data and datetime types."""
        first, second = BaseModel(), BaseModel()
        first.name = "My First Model"
        second.my_number = 89
        expected = {key: value.to_dict()
                    for key, value in models.storage.all().items()}
        models.storage.save()
        models.storage.all().clear()
        models.storage.reload()
        self.assertEqual(set(models.storage.all()), set(expected))
        for key, instance in models.storage.all().items():
            self.assertIsInstance(instance, BaseModel)
            self.assertEqual(instance.to_dict(), expected[key])
        self.assertIsNot(models.storage.all()["BaseModel." + first.id], first)

    def test_repeated_reload_does_not_duplicate_objects(self):
        """Reloading twice still leaves one entry per saved object."""
        BaseModel().save()
        models.storage.reload()
        models.storage.reload()
        self.assertEqual(len(models.storage.all()), 1)

    def test_save_and_reload_unicode_and_nested_values(self):
        """JSON preserves Unicode text and nested simple values."""
        instance = BaseModel()
        instance.name = "Lagos – Àyọ̀"
        instance.details = {"numbers": [1, 2.5], "active": True, "note": None}
        instance.save()
        expected = instance.to_dict()
        models.storage.all().clear()
        models.storage.reload()
        self.assertEqual(models.storage.all()["BaseModel." + instance.id]
                         .to_dict(), expected)

    def test_invalid_json_is_reported(self):
        """Malformed JSON is not treated as a missing file."""
        with open(self.path, "w", encoding="utf-8") as stream:
            stream.write("{ invalid json")
        with self.assertRaises(ValueError):
            models.storage.reload()

    def test_permission_error_is_reported(self):
        """Read permission failures are not hidden by missing-file logic."""
        with patch("builtins.open", side_effect=PermissionError):
            with self.assertRaises(PermissionError):
                models.storage.reload()

    def test_unknown_class_is_reported_without_executing_code(self):
        """Class names must be in the explicit registry."""
        data = BaseModel().to_dict()
        data["__class__"] = "UnregisteredClass"
        with open(self.path, "w", encoding="utf-8") as stream:
            json.dump({"Unknown.1": data}, stream)
        with self.assertRaises(KeyError):
            models.storage.reload()
