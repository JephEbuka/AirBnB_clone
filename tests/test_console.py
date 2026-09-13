#!/usr/bin/python3
"""Verify command behavior, help, validation and persistent changes."""

from datetime import timedelta
import io
import json
from uuid import UUID

from console import HBNBCommand
from models import storage
from models.base_model import BaseModel
from tests.helpers import StorageTestCase


class TestConsole(StorageTestCase):
    """Run console commands against isolated storage."""

    def setUp(self):
        """Create a console that writes to an in-memory text stream."""
        super().setUp()
        self.output = io.StringIO()
        self.console = HBNBCommand(stdout=self.output)

    def execute(self, command):
        """Run a command and return its output without previous output."""
        self.output.seek(0)
        self.output.truncate(0)
        self.console.onecmd(command)
        return self.output.getvalue()

    def test_prompt(self):
        """The expected project prompt is configured."""
        self.assertEqual(self.console.prompt, "(hbnb) ")

    def test_quit_and_eof_stop_console(self):
        """Both exit mechanisms return a true stop value."""
        self.assertTrue(self.console.onecmd("quit"))
        self.assertTrue(self.console.onecmd("EOF"))

    def test_help_lists_commands(self):
        """Help lists each supported command."""
        output = self.execute("help")
        for command in ("create", "show", "all", "update", "destroy", "quit"):
            self.assertIn(command, output)
        self.assertIn("create BaseModel", self.execute("help create"))

    def test_empty_line_does_not_repeat_create(self):
        """A blank input cannot create another object accidentally."""
        self.execute("create BaseModel")
        self.assertEqual(self.execute(""), "")
        self.assertEqual(len(storage.all()), 1)

    def test_create_prints_uuid_and_saves(self):
        """Creation prints an ID and persists its new instance."""
        identifier = self.execute("create BaseModel").strip()
        self.assertEqual(UUID(identifier).version, 4)
        with open(self.path, encoding="utf-8") as stream:
            self.assertIn("BaseModel." + identifier, json.load(stream))

    def test_class_errors(self):
        """Commands report absent or unsupported classes consistently."""
        for command in ("create", "show", "destroy", "update"):
            with self.subTest(command=command):
                self.assertEqual(self.execute(command),
                                 "** class name missing **\n")
                self.assertEqual(self.execute(command + " Unknown"),
                                 "** class doesn't exist **\n")
        self.assertEqual(self.execute("all Unknown"),
                         "** class doesn't exist **\n")

    def test_unmatched_quotes_report_invalid_syntax(self):
        """Badly quoted input reports an error instead of crashing."""
        for command in ("create", "show", "destroy", "update", "all"):
            with self.subTest(command=command):
                self.assertEqual(self.execute(command + ' "BaseModel'),
                                 "** invalid syntax **\n")

    def test_instance_errors(self):
        """Commands distinguish missing IDs from absent instances."""
        for command in ("show", "destroy", "update"):
            with self.subTest(command=command):
                self.assertEqual(self.execute(command + " BaseModel"),
                                 "** instance id missing **\n")
                self.assertEqual(self.execute(command + " BaseModel absent"),
                                 "** no instance found **\n")

    def test_show_displays_instance(self):
        """Show prints the requested object's string representation."""
        instance = BaseModel()
        self.assertEqual(self.execute("show BaseModel " + instance.id),
                         str(instance) + "\n")

    def test_all_empty_and_populated(self):
        """Listing shows no objects initially, then every created object."""
        self.assertEqual(self.execute("all"), "[]\n")
        first, second = BaseModel(), BaseModel()
        for command in ("all", "all BaseModel"):
            output = self.execute(command)
            self.assertIn(first.id, output)
            self.assertIn(second.id, output)

    def test_destroy_removes_and_persists(self):
        """Destroy removes only its target from memory and disk."""
        first, second = BaseModel(), BaseModel()
        self.assertEqual(self.execute("destroy BaseModel " + first.id), "")
        self.assertNotIn("BaseModel." + first.id, storage.all())
        with open(self.path, encoding="utf-8") as stream:
            self.assertEqual(set(json.load(stream)),
                             {"BaseModel." + second.id})

    def test_update_requires_attribute_and_value(self):
        """Update reports which required argument is missing."""
        command = "update BaseModel " + BaseModel().id
        self.assertEqual(self.execute(command),
                         "** attribute name missing **\n")
        self.assertEqual(self.execute(command + " name"),
                         "** value missing **\n")

    def test_update_quoted_text_integer_and_float(self):
        """Attribute changes keep spaces and the supported numeric types."""
        instance = BaseModel()
        command = "update BaseModel " + instance.id
        self.execute(command + ' name "My First Model"')
        self.execute(command + " my_number 89")
        self.execute(command + " rating 4.5")
        self.assertEqual(instance.name, "My First Model")
        self.assertIs(type(instance.my_number), int)
        self.assertEqual(instance.my_number, 89)
        self.assertIs(type(instance.rating), float)
        self.assertEqual(instance.rating, 4.5)
        with open(self.path, encoding="utf-8") as stream:
            saved = json.load(stream)["BaseModel." + instance.id]
        self.assertEqual(saved, instance.to_dict())

    def test_update_refreshes_timestamp(self):
        """An update saves the model and refreshes its modification time."""
        instance = BaseModel()
        instance.updated_at -= timedelta(days=1)
        earlier = instance.updated_at
        self.execute("update BaseModel {} name Updated".format(instance.id))
        self.assertGreater(instance.updated_at, earlier)

    def test_update_protects_identity_timestamps_and_methods(self):
        """Reserved fields cannot invalidate an object's identity or API."""
        instance = BaseModel()
        original = instance.__dict__.copy()
        for name in ("id", "created_at", "updated_at", "__class__", "save",
                     "to_dict", "_hidden"):
            self.execute("update BaseModel {} {} changed".format(instance.id,
                                                                 name))
        self.assertEqual(instance.__dict__, original)

    def test_unknown_command(self):
        """Unknown commands return the standard interpreter error."""
        self.assertIn("Unknown syntax", self.execute("unknown_command"))

    def test_create_show_update_destroy_for_every_class(self):
        """All model classes support the required CRUD commands."""
        for name in ("User", "Place", "State", "City", "Amenity", "Review"):
            with self.subTest(model=name):
                identifier = self.execute("create " + name).strip()
                key = "{}.{}".format(name, identifier)
                self.assertIn(key, storage.all())
                output = self.execute("show {} {}".format(name, identifier))
                self.assertIn("[" + name + "]", output)
                self.execute('update {} {} custom_text "Saved value"'.format(
                    name, identifier))
                self.assertEqual(storage.all()[key].custom_text, "Saved value")
                storage.reload()
                self.assertEqual(storage.all()[key].custom_text, "Saved value")
                self.assertIn(identifier, self.execute("all " + name))
                self.execute("destroy {} {}".format(name, identifier))
                self.assertNotIn(key, storage.all())

    def test_all_filters_mixed_model_classes(self):
        """A class-filtered list excludes other model classes."""
        user_id = self.execute("create User").strip()
        place_id = self.execute("create Place").strip()
        output = self.execute("all User")
        self.assertIn(user_id, output)
        self.assertNotIn(place_id, output)
        self.assertIn(place_id, self.execute("all"))

    def test_update_accepts_declared_string_fields(self):
        """Public class defaults can be edited and keep their string type."""
        identifier = self.execute("create User").strip()
        self.execute('update User {} first_name "Ada Lovelace"'.format(
            identifier))
        self.execute('update User {} password "0123"'.format(identifier))
        user = storage.all()["User." + identifier]
        self.assertEqual(user.first_name, "Ada Lovelace")
        self.assertEqual(user.password, "0123")

    def test_update_preserves_declared_numeric_types(self):
        """Place number fields use their declared integer or float type."""
        identifier = self.execute("create Place").strip()
        self.execute("update Place {} number_rooms 3".format(identifier))
        self.execute("update Place {} latitude 6".format(identifier))
        place = storage.all()["Place." + identifier]
        self.assertEqual(place.number_rooms, 3)
        self.assertIs(type(place.number_rooms), int)
        self.assertEqual(place.latitude, 6.0)
        self.assertIs(type(place.latitude), float)

    def test_invalid_values_do_not_change_typed_fields(self):
        """Invalid input cannot corrupt a typed public default."""
        identifier = self.execute("create Place").strip()
        for name, value in (("number_rooms", "invalid"),
                            ("latitude", "invalid"),
                            ("amenity_ids", "invalid")):
            with self.subTest(attribute=name):
                output = self.execute("update Place {} {} {}".format(
                    identifier, name, value))
                self.assertEqual(output, "** invalid attribute value **\n")
        place = storage.all()["Place." + identifier]
        self.assertEqual(place.number_rooms, 0)
        self.assertEqual(place.latitude, 0.0)
        self.assertEqual(place.amenity_ids, [])
