# -*- coding: utf-8 -*-
from typing import Union, List


class Payload():
    def __init__(self, message: bytes = b''):
        self.message = message
        self.length = len(self.message)

    def __call__(self):
        return self.message

    def is_valid(self):
        return 0 <= self.length <= 114
