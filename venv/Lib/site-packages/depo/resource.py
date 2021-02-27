# -*- coding: utf-8 -*-

from __future__ import absolute_import, division, print_function

import depo
import json
import requests

from decimal import Decimal
from .utils import JSONEncoder
from .version import VERSION


class Requestor:
    def request(self, method, data={}, timeout=30):
        if not isinstance(depo.api_credentials, tuple):
            raise depo.error.APIError(
                "Invalid credentials to DEPO service provided "
                "(expected two-part tuple with `username` "
                "and `password` to cleint zone)."
            )

        url = "%s%s" % (depo.DEPO_API_ENDPOINT, method)

        headers = {
            "User-Agent": "depo-python/" + VERSION,
            "Content-Type": "application/json",
        }

        try:
            if data:
                response = requests.post(
                    url=url,
                    headers=headers,
                    data=json.dumps(data, cls=JSONEncoder),
                    timeout=timeout,
                    auth=depo.api_credentials,
                )
            else:
                response = requests.get(
                    url=url,
                    headers=headers,
                    timeout=timeout,
                    auth=depo.api_credentials,
                )
        except Exception as e:
            self._handle_request_error(e)

        return response

    def _handle_request_error(self, e):
        if isinstance(e, requests.exceptions.RequestException):
            err = "%s: %s" % (type(e).__name__, str(e))
        else:
            err = "A %s was raised" % (type(e).__name__,)

            if str(e):
                err += " with error message %s" % (str(e),)
            else:
                err += " with no error message"

        msg = "Network error: %s" % (err,)

        raise depo.error.APIConnectionError(msg)


class Order:
    @classmethod
    def create(
        cls,
        place,
        recipient_name,
        recipient_phone,
        recipient_email,
        total_amount,
        products_amount,
        reference=None,
    ):
        if (
            isinstance(place, int)
            or isinstance(place, str)
            or isinstance(place, unicode)
        ):
            place = depo.Place.get(place)

        if not place.is_output:
            raise depo.error.PlaceUnavailableError(
                "Selected place %s is not available" % place.name
            )

        data = {
            "target": place.id,
            "recipient_name": recipient_name,
            "recipient_phone": recipient_phone,
            "recipient_email": recipient_email,
            "cod": total_amount,
            "insurance": products_amount,
        }

        if reference:
            data["sender_reference"] = unicode(reference)

        client = Requestor()
        response = client.request("packages/send", data=data)
        return response.json()

    @classmethod
    def get(cls, order_id):
        client = Requestor()
        response = client.request("packages/%s" % order_id)
        return response.json()

    @classmethod
    def cancel(cls, order_id):
        client = Requestor()
        response = client.request("packages/cancel", data={"number": order_id})
        return response.json()


class Place:
    def __init__(self, data={}):
        self.id = data.get("id")
        self.name = data.get("name", "")
        self.street = data.get("street", "")
        self.zip = str(data.get("zip", ""))
        self.city = data.get("city", "")
        self.latitude = Decimal(data.get("latitude", 0)).quantize(
            Decimal(".0000001")
        )
        self.longitude = Decimal(data.get("longitude", 0)).quantize(
            Decimal(".0000001")
        )
        self.opening_hours = data.get("open_hours", "")
        self.image = data.get("image")

        self.is_output = True if data.get("is_output", False) else False
        self.is_input = True if data.get("is_input", False) else False

    @property
    def is_active(self):
        return self.is_output

    def __str__(self):
        return str(self.__dict__)

    @classmethod
    def get(cls, place_id):
        client = Requestor()
        response = client.request("places/%s" % place_id)

        return Place(response.json())

    @classmethod
    def all(cls):
        client = Requestor()
        response = client.request("places")
        data = response.json()

        if "_embedded" not in data.keys() or "places" not in data["_embedded"]:
            raise depo.error.APIError(
                "Invalid response object from API: %s" % response.text
            )

        places = []

        for place in data["_embedded"]["places"]:
            if place.get("is_output"):
                places.append(Place(place))

        return places
