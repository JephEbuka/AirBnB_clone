#!/usr/bin/python3
"""Keep every test's storage separate from the application's data."""

import os
import tempfile
import unittest
from unittest.mock import patch

from models.engine.file_storage import FileStorage


class StorageTestCase(unittest.TestCase):
    """Provide a fresh shared object registry and temporary JSON path."""

    def setUp(self):
        """Replace storage state for this test and restore it afterward."""
        temporary = tempfile.TemporaryDirectory()
        self.addCleanup(temporary.cleanup)
        self.path = os.path.join(temporary.name, "file.json")
        objects_patch = patch.object(FileStorage, "_FileStorage__objects", {})
        path_patch = patch.object(FileStorage, "_FileStorage__file_path",
                                  self.path)
        objects_patch.start()
        self.addCleanup(objects_patch.stop)
        path_patch.start()
        self.addCleanup(path_patch.stop)
