# -*- coding: utf-8 -*-

from __future__ import absolute_import, division, print_function


class DepoError(Exception):
    def __init__(self, message=None, http_body=None):
        super(DepoError, self).__init__(message)

        self.http_body = http_body


class PlaceUnavailableError(DepoError):
    pass


class APIError(DepoError):
    pass


class APIConnectionError(APIError):
    pass
