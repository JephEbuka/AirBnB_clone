#!/usr/bin/python3
"""Define the user model."""

from models.base_model import BaseModel


class User(BaseModel):
    """Represent a user with contact details and a name."""

    email = ""
    password = ""
    first_name = ""
    last_name = ""
