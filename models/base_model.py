#!/usr/bin/python3
"""Define the attributes and persistence shared by model instances."""

from datetime import datetime
import uuid

import models


class BaseModel:
    """Represent an object with a unique ID and creation/update times."""

    def __init__(self, *args, **kwargs):
        """Restore attributes from kwargs, or register a new instance."""
        if kwargs:
            for key, value in kwargs.items():
                if key == "__class__":
                    continue
                if key in ("created_at", "updated_at"):
                    try:
                        value = datetime.strptime(
                            value, "%Y-%m-%dT%H:%M:%S.%f")
                    except ValueError:
                        value = datetime.strptime(value, "%Y-%m-%dT%H:%M:%S")
                setattr(self, key, value)
        else:
            self.id = str(uuid.uuid4())
            self.created_at = datetime.now()
            self.updated_at = datetime.now()
            models.storage.new(self)

    def __str__(self):
        """Return the class, ID and instance attribute dictionary."""
        return "[{}] ({}) {}".format(
            type(self).__name__, self.id, self.__dict__)

    def save(self):
        """Update the modification time and persist registered objects."""
        self.updated_at = datetime.now()
        models.storage.save()

    def to_dict(self):
        """Return a new dictionary containing JSON-compatible attributes."""
        result = self.__dict__.copy()
        result["__class__"] = type(self).__name__
        result["created_at"] = self.created_at.isoformat()
        result["updated_at"] = self.updated_at.isoformat()
        return result
