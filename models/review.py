#!/usr/bin/python3
"""Define the review model."""

from models.base_model import BaseModel


class Review(BaseModel):
    """Represent a user's written review of an accommodation."""

    place_id = ""
    user_id = ""
    text = ""
