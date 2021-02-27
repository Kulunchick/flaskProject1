# -*- coding: utf-8 -*-

from __future__ import absolute_import, division, print_function

import json

from decimal import Decimal


class JSONEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, Decimal):
            return str(obj)
        else:
            return super(JSONEncoder, self).default(obj)
