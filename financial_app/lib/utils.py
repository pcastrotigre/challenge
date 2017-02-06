from enum import Enum
import json


class RpcType(Enum):
    STOCK = 1
    DAYS_RANGE = 2


class Error:
    def __init__(self, message):
        self.message = message

    def __str__(self):
        return json.dumps({"error": self.message})


class Response:
    def __init__(self, message):
        self.message = message

    def __str__(self):
        return json.dumps({"message": self.message})
