#!/usr/bin/python3
"""Define the amenity model."""

from models.base_model import BaseModel


class Amenity(BaseModel):
    """Represent an amenity that can be associated with an accommodation."""

    name = ""
