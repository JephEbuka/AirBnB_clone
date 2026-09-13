#!/usr/bin/python3
"""Verify the Review model's defaults and inherited behavior."""

from models.review import Review
from tests.helpers import StorageTestCase
from tests.model_cases import ModelContractMixin


class TestReview(ModelContractMixin, StorageTestCase):
    """Exercise Review independently and through shared file storage."""

    model_class = Review
    defaults = {"place_id": "", "user_id": "", "text": ""}
