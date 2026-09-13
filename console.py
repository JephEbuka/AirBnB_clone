#!/usr/bin/python3
"""Provide a command interpreter for the AirBnB clone models."""

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
    """Create, inspect, update and delete persisted model objects."""

    prompt = "(hbnb) "
    classes = {
        "BaseModel": BaseModel,
        "User": User,
        "Place": Place,
        "State": State,
        "City": City,
        "Amenity": Amenity,
        "Review": Review,
    }

    def emptyline(self):
        """Ignore an empty line instead of repeating the previous command."""
        pass

    def do_quit(self, arg):
        """Exit the interpreter: quit"""
        return True

    def do_EOF(self, arg):
        """Exit the interpreter at end of input."""
        self.stdout.write("\n")
        return True

    def _arguments(self, arg):
        """Parse shell-style arguments and validate the class name."""
        try:
            arguments = shlex.split(arg)
        except ValueError:
            self.stdout.write("** invalid syntax **\n")
            return None
        if not arguments:
            self.stdout.write("** class name missing **\n")
            return None
        if arguments[0] not in self.classes:
            self.stdout.write("** class doesn't exist **\n")
            return None
        return arguments

    def _instance(self, arguments):
        """Find a named instance and report a missing ID or object."""
        if len(arguments) < 2:
            self.stdout.write("** instance id missing **\n")
            return None
        key = "{}.{}".format(arguments[0], arguments[1])
        instance = storage.all().get(key)
        if instance is None:
            self.stdout.write("** no instance found **\n")
        return instance

    def do_create(self, arg):
        """Create and save an object: create BaseModel"""
        arguments = self._arguments(arg)
        if arguments is None:
            return
        instance = self.classes[arguments[0]]()
        instance.save()
        self.stdout.write(instance.id + "\n")

    def do_show(self, arg):
        """Display an object: show BaseModel <id>"""
        arguments = self._arguments(arg)
        if arguments is None:
            return
        instance = self._instance(arguments)
        if instance is not None:
            self.stdout.write(str(instance) + "\n")

    def do_destroy(self, arg):
        """Delete and persist removal of an object: destroy BaseModel <id>"""
        arguments = self._arguments(arg)
        if arguments is None:
            return
        instance = self._instance(arguments)
        if instance is not None:
            key = "{}.{}".format(arguments[0], instance.id)
            del storage.all()[key]
            storage.save()

    def do_all(self, arg):
        """List objects: all [BaseModel]"""
        class_name = None
        if arg.strip():
            arguments = self._arguments(arg)
            if arguments is None:
                return
            class_name = arguments[0]
        objects = [str(obj) for obj in storage.all().values()
                   if class_name is None or type(obj).__name__ == class_name]
        self.stdout.write(str(objects) + "\n")

    def do_update(self, arg):
        """Set an attribute: update BaseModel <id> <attribute> <value>"""
        arguments = self._arguments(arg)
        if arguments is None:
            return
        instance = self._instance(arguments)
        if instance is None:
            return
        if len(arguments) < 3:
            self.stdout.write("** attribute name missing **\n")
            return
        if len(arguments) < 4:
            self.stdout.write("** value missing **\n")
            return
        name, value = arguments[2:4]
        if name in ("id", "created_at", "updated_at"):
            return
        class_value = getattr(type(instance), name, None)
        if name.startswith("_") or callable(class_value):
            self.stdout.write("** invalid attribute name **\n")
            return
        if class_value is not None:
            value_type = type(class_value)
            if value_type not in (str, int, float):
                self.stdout.write("** invalid attribute value **\n")
                return
            try:
                value = value_type(value)
            except (TypeError, ValueError, OverflowError):
                self.stdout.write("** invalid attribute value **\n")
                return
        else:
            try:
                value = int(value)
            except ValueError:
                try:
                    value = float(value)
                except ValueError:
                    pass
        setattr(instance, name, value)
        instance.save()


if __name__ == "__main__":
    HBNBCommand().cmdloop()
