#!/usr/bin/python3
"""Create and reload the application's shared file storage."""

from models.engine.file_storage import FileStorage

storage = FileStorage()
storage.reload()
