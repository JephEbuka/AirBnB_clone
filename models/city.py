#!/usr/bin/python3
"""Define the city model."""

from models.base_model import BaseModel


class City(BaseModel):
    """Represent a city and its parent state."""

    state_id = ""
    name = ""
