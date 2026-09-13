#!/usr/bin/python3
"""Verify the User model's defaults and inherited behavior."""

from models.user import User
from tests.helpers import StorageTestCase
from tests.model_cases import ModelContractMixin


class TestUser(ModelContractMixin, StorageTestCase):
    """Exercise User independently and through shared file storage."""

    model_class = User
    defaults = {"email": "", "password": "", "first_name": "", "last_name": ""}
