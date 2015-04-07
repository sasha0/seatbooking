# -*- coding: utf-8 -*-
import json
from bson.objectid import ObjectId


class CustomEncoder(json.JSONEncoder):
    def default(self, o):
        if isinstance(o, ObjectId):
            return str(o)
        return super(CustomEncoder, self).default(o)