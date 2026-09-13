#!/usr/bin/env bash
# AirBnB_clone Console 1.0 complete setup
# Covers:
#   Console 0.0
#   Console 0.1
#   First User
#   More classes
#   Console 1.0
#
# Run from the ROOT of your AirBnB_clone repository:
#   chmod +x setup_airbnb_console_1_0.sh
#   ./setup_airbnb_console_1_0.sh

set -e

mkdir -p models/engine
mkdir -p tests/test_models/test_engine

cat > models/__init__.py <<'EOF'
#!/usr/bin/python3
"""Initialize the models package."""

from models.engine.file_storage import FileStorage

storage = FileStorage()
storage.reload()
EOF

cat > models/base_model.py <<'EOF'
#!/usr/bin/python3
"""Defines the BaseModel class."""

from datetime import datetime
import uuid
import models


class BaseModel:
    """Defines common attributes and methods for all models."""

    def __init__(self, *args, **kwargs):
        """Initialize a BaseModel instance."""
        if kwargs:
            for key, value in kwargs.items():
                if key == "__class__":
                    continue
                if key in ("created_at", "updated_at"):
                    value = datetime.fromisoformat(value)
                setattr(self, key, value)
        else:
            self.id = str(uuid.uuid4())
            self.created_at = datetime.now()
            self.updated_at = datetime.now()
            models.storage.new(self)

    def __str__(self):
        """Return the string representation of the instance."""
        return "[{}] ({}) {}".format(
            self.__class__.__name__, self.id, self.__dict__
        )

    def save(self):
        """Update updated_at and save objects to file storage."""
        self.updated_at = datetime.now()
        models.storage.save()

    def to_dict(self):
        """Return a dictionary representation of the instance."""
        result = self.__dict__.copy()
        result["__class__"] = self.__class__.__name__

        if "created_at" in result:
            result["created_at"] = result["created_at"].isoformat()

        if "updated_at" in result:
            result["updated_at"] = result["updated_at"].isoformat()

        return result
EOF

cat > models/user.py <<'EOF'
#!/usr/bin/python3
"""Defines the User class."""

from models.base_model import BaseModel


class User(BaseModel):
    """Represent a user."""

    email = ""
    password = ""
    first_name = ""
    last_name = ""
EOF

cat > models/state.py <<'EOF'
#!/usr/bin/python3
"""Defines the State class."""

from models.base_model import BaseModel


class State(BaseModel):
    """Represent a state."""

    name = ""
EOF

cat > models/city.py <<'EOF'
#!/usr/bin/python3
"""Defines the City class."""

from models.base_model import BaseModel


class City(BaseModel):
    """Represent a city."""

    state_id = ""
    name = ""
EOF

cat > models/amenity.py <<'EOF'
#!/usr/bin/python3
"""Defines the Amenity class."""

from models.base_model import BaseModel


class Amenity(BaseModel):
    """Represent an amenity."""

    name = ""
EOF

cat > models/place.py <<'EOF'
#!/usr/bin/python3
"""Defines the Place class."""

from models.base_model import BaseModel


class Place(BaseModel):
    """Represent a place."""

    city_id = ""
    user_id = ""
    name = ""
    description = ""
    number_rooms = 0
    number_bathrooms = 0
    max_guest = 0
    price_by_night = 0
    latitude = 0.0
    longitude = 0.0
    amenity_ids = []
EOF

cat > models/review.py <<'EOF'
#!/usr/bin/python3
"""Defines the Review class."""

from models.base_model import BaseModel


class Review(BaseModel):
    """Represent a review."""

    place_id = ""
    user_id = ""
    text = ""
EOF

cat > models/engine/__init__.py <<'EOF'
#!/usr/bin/python3
"""Initialize the storage engine package."""
EOF

cat > models/engine/file_storage.py <<'EOF'
#!/usr/bin/python3
"""Defines JSON file storage for AirBnB model instances."""

import json


class FileStorage:
    """Serialize instances to JSON and deserialize JSON to instances."""

    __file_path = "file.json"
    __objects = {}

    def all(self):
        """Return all stored objects."""
        return self.__objects

    def new(self, obj):
        """Store a new object using <class name>.<id> as the key."""
        key = "{}.{}".format(obj.__class__.__name__, obj.id)
        self.__objects[key] = obj

    def save(self):
        """Serialize all stored objects to the JSON file."""
        serialized = {
            key: obj.to_dict() for key, obj in self.__objects.items()
        }

        with open(self.__file_path, "w", encoding="utf-8") as file:
            json.dump(serialized, file)

    def reload(self):
        """Deserialize the JSON file into model instances."""
        try:
            with open(self.__file_path, "r", encoding="utf-8") as file:
                serialized = json.load(file)
        except FileNotFoundError:
            return

        from models.amenity import Amenity
        from models.base_model import BaseModel
        from models.city import City
        from models.place import Place
        from models.review import Review
        from models.state import State
        from models.user import User

        classes = {
            "Amenity": Amenity,
            "BaseModel": BaseModel,
            "City": City,
            "Place": Place,
            "Review": Review,
            "State": State,
            "User": User,
        }

        for key, value in serialized.items():
            class_name = value.get("__class__")
            class_type = classes.get(class_name)
            if class_type is not None:
                self.__objects[key] = class_type(**value)
EOF

cat > console.py <<'EOF'
#!/usr/bin/python3
"""Entry point for the AirBnB command interpreter."""

import cmd
import shlex

from models import storage
from models.amenity import Amenity
from models.base_model import BaseModel
from models.city import City
from models.place import Place
from models.review import Review
from models.state import State
from models.user import User


class HBNBCommand(cmd.Cmd):
    """AirBnB command interpreter."""

    prompt = "(hbnb) "

    __classes = {
        "Amenity": Amenity,
        "BaseModel": BaseModel,
        "City": City,
        "Place": Place,
        "Review": Review,
        "State": State,
        "User": User,
    }

    def emptyline(self):
        """Do nothing when an empty line is entered."""
        pass

    def do_quit(self, arg):
        """Quit command to exit the program."""
        return True

    def do_EOF(self, arg):
        """EOF command to exit the program."""
        print()
        return True

    def do_create(self, arg):
        """Create a new instance, save it, and print its id."""
        args = shlex.split(arg)

        if not args:
            print("** class name missing **")
            return

        class_name = args[0]

        if class_name not in self.__classes:
            print("** class doesn't exist **")
            return

        obj = self.__classes[class_name]()
        obj.save()
        print(obj.id)

    def do_show(self, arg):
        """Print the string representation of an instance."""
        args = shlex.split(arg)

        if not args:
            print("** class name missing **")
            return

        class_name = args[0]

        if class_name not in self.__classes:
            print("** class doesn't exist **")
            return

        if len(args) < 2:
            print("** instance id missing **")
            return

        key = "{}.{}".format(class_name, args[1])
        obj = storage.all().get(key)

        if obj is None:
            print("** no instance found **")
            return

        print(obj)

    def do_destroy(self, arg):
        """Delete an instance and save the storage change."""
        args = shlex.split(arg)

        if not args:
            print("** class name missing **")
            return

        class_name = args[0]

        if class_name not in self.__classes:
            print("** class doesn't exist **")
            return

        if len(args) < 2:
            print("** instance id missing **")
            return

        key = "{}.{}".format(class_name, args[1])
        objects = storage.all()

        if key not in objects:
            print("** no instance found **")
            return

        del objects[key]
        storage.save()

    def do_all(self, arg):
        """Print all instances, optionally filtered by class."""
        args = shlex.split(arg)

        if args and args[0] not in self.__classes:
            print("** class doesn't exist **")
            return

        class_name = args[0] if args else None
        output = []

        for obj in storage.all().values():
            if class_name is None or obj.__class__.__name__ == class_name:
                output.append(str(obj))

        print(output)

    def do_update(self, arg):
        """Update one attribute on an instance and save the change."""
        args = shlex.split(arg)

        if not args:
            print("** class name missing **")
            return

        class_name = args[0]

        if class_name not in self.__classes:
            print("** class doesn't exist **")
            return

        if len(args) < 2:
            print("** instance id missing **")
            return

        key = "{}.{}".format(class_name, args[1])
        obj = storage.all().get(key)

        if obj is None:
            print("** no instance found **")
            return

        if len(args) < 3:
            print("** attribute name missing **")
            return

        if len(args) < 4:
            print("** value missing **")
            return

        attr_name = args[2]
        value = args[3]

        if hasattr(obj, attr_name):
            current_value = getattr(obj, attr_name)
            value_type = type(current_value)

            if value_type is int:
                value = int(value)
            elif value_type is float:
                value = float(value)
            elif value_type is str:
                value = str(value)

        setattr(obj, attr_name, value)
        obj.save()


if __name__ == '__main__':
    HBNBCommand().cmdloop()
EOF

cat > tests/__init__.py <<'EOF'
#!/usr/bin/python3
"""Initialize tests."""
EOF

mkdir -p tests/test_models
cat > tests/test_models/__init__.py <<'EOF'
#!/usr/bin/python3
"""Initialize model tests."""
EOF

cat > tests/test_models/test_engine/__init__.py <<'EOF'
#!/usr/bin/python3
"""Initialize storage engine tests."""
EOF

cat > tests/test_models/test_models.py <<'EOF'
#!/usr/bin/python3
"""Tests for AirBnB model classes."""

import unittest

from models.amenity import Amenity
from models.base_model import BaseModel
from models.city import City
from models.place import Place
from models.review import Review
from models.state import State
from models.user import User


class TestModels(unittest.TestCase):
    """Test the required AirBnB model classes."""

    def test_user_inherits_base_model(self):
        """User should inherit BaseModel."""
        self.assertIsInstance(User(), BaseModel)

    def test_user_defaults(self):
        """User should define required default attributes."""
        obj = User()
        self.assertEqual(obj.email, "")
        self.assertEqual(obj.password, "")
        self.assertEqual(obj.first_name, "")
        self.assertEqual(obj.last_name, "")

    def test_state_defaults(self):
        """State should define name."""
        self.assertEqual(State().name, "")

    def test_city_defaults(self):
        """City should define state_id and name."""
        obj = City()
        self.assertEqual(obj.state_id, "")
        self.assertEqual(obj.name, "")

    def test_amenity_defaults(self):
        """Amenity should define name."""
        self.assertEqual(Amenity().name, "")

    def test_place_defaults(self):
        """Place should define all required attributes."""
        obj = Place()
        self.assertEqual(obj.city_id, "")
        self.assertEqual(obj.user_id, "")
        self.assertEqual(obj.name, "")
        self.assertEqual(obj.description, "")
        self.assertEqual(obj.number_rooms, 0)
        self.assertEqual(obj.number_bathrooms, 0)
        self.assertEqual(obj.max_guest, 0)
        self.assertEqual(obj.price_by_night, 0)
        self.assertEqual(obj.latitude, 0.0)
        self.assertEqual(obj.longitude, 0.0)
        self.assertEqual(obj.amenity_ids, [])

    def test_review_defaults(self):
        """Review should define required attributes."""
        obj = Review()
        self.assertEqual(obj.place_id, "")
        self.assertEqual(obj.user_id, "")
        self.assertEqual(obj.text, "")


if __name__ == "__main__":
    unittest.main()
EOF

cat > tests/test_models/test_engine/test_file_storage_all_models.py <<'EOF'
#!/usr/bin/python3
"""Tests FileStorage support for all required models."""

import json
import os
import unittest

from models.amenity import Amenity
from models.city import City
from models.engine.file_storage import FileStorage
from models.place import Place
from models.review import Review
from models.state import State
from models.user import User


class TestFileStorageAllModels(unittest.TestCase):
    """Test FileStorage serialization for all model classes."""

    def setUp(self):
        """Reset FileStorage object dictionary before each test."""
        FileStorage._FileStorage__objects = {}
        self.storage = FileStorage()

    def tearDown(self):
        """Remove the storage file after each test."""
        path = FileStorage._FileStorage__file_path
        if os.path.exists(path):
            os.remove(path)

    def test_save_all_models(self):
        """Save one instance of each model as JSON."""
        instances = [
            User(),
            State(),
            City(),
            Amenity(),
            Place(),
            Review(),
        ]

        for obj in instances:
            self.storage.new(obj)

        self.storage.save()

        path = FileStorage._FileStorage__file_path
        with open(path, "r", encoding="utf-8") as file:
            data = json.load(file)

        for obj in instances:
            key = "{}.{}".format(obj.__class__.__name__, obj.id)
            self.assertIn(key, data)

    def test_reload_all_models(self):
        """Reload all supported model classes from JSON."""
        instances = [
            User(),
            State(),
            City(),
            Amenity(),
            Place(),
            Review(),
        ]

        for obj in instances:
            self.storage.new(obj)

        self.storage.save()
        FileStorage._FileStorage__objects = {}

        reloaded = FileStorage()
        reloaded.reload()

        for obj in instances:
            key = "{}.{}".format(obj.__class__.__name__, obj.id)
            self.assertIn(key, reloaded.all())
            self.assertEqual(
                reloaded.all()[key].__class__.__name__,
                obj.__class__.__name__,
            )


if __name__ == "__main__":
    unittest.main()
EOF

# Keep Python cache and runtime storage out of Git.
if [ ! -f .gitignore ]; then
    touch .gitignore
fi

grep -qxF '__pycache__/' .gitignore || echo '__pycache__/' >> .gitignore
grep -qxF '*.pyc' .gitignore || echo '*.pyc' >> .gitignore
grep -qxF 'file.json' .gitignore || echo 'file.json' >> .gitignore

chmod +x console.py

echo
echo "AirBnB Console 1.0 files created successfully."
echo
echo "Run:"
echo "  python3 -m unittest discover tests"
echo "  pycodestyle console.py models tests"
echo
echo "Quick console check:"
echo '  printf "create BaseModel\nall BaseModel\nquit\n" | ./console.py'