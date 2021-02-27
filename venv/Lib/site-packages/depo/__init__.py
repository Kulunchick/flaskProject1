# -*- coding: utf-8 -*-

from .error import (  # noqa: F401
    APIConnectionError,
    APIError,
    DepoError,
    PlaceUnavailableError,
)
from .resource import Order, Place  # noqa: F401
from .utils import JSONEncoder  # noqa: F401

# Configuration variables
api_credentials = None

DEPO_API_ENDPOINT = "https://admin.depo.sk/v2/api/"
