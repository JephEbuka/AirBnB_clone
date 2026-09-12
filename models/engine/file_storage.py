#!/usr/bin/python3
"""Serialize model instances to JSON and restore them from disk."""

import json


class FileStorage:
    """Keep registered objects in memory and persist them in file.json."""

    __file_path = "file.json"
    __objects = {}

    def all(self):
        """Return the live dictionary of registered instances."""
        return self.__objects

    def new(self, obj):
        """Register an instance using its class name and ID as its key."""
        key = "{}.{}".format(type(obj).__name__, obj.id)
        self.__objects[key] = obj

    def save(self):
        """Write all registered instances as a JSON object."""
        data = {key: obj.to_dict() for key, obj in self.__objects.items()}
        with open(self.__file_path, "w", encoding="utf-8") as stream:
            json.dump(data, stream)

    def reload(self):
        """Restore all supported model classes; ignore a missing file."""
        try:
            with open(self.__file_path, "r", encoding="utf-8") as stream:
                data = json.load(stream)
        except FileNotFoundError:
            return

        # Import after models.storage exists to avoid circular imports.
        from models.amenity import Amenity
        from models.base_model import BaseModel
        from models.city import City
        from models.place import Place
        from models.review import Review
        from models.state import State
        from models.user import User

        classes = {
            "BaseModel": BaseModel,
            "User": User,
            "Place": Place,
            "State": State,
            "City": City,
            "Amenity": Amenity,
            "Review": Review,
        }
        restored = {}
        for key, attributes in data.items():
            model_class = classes[attributes["__class__"]]
            restored[key] = model_class(**attributes)
        self.__objects.update(restored)
