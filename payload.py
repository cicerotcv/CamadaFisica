# -*- coding: utf-8 -*-
from constants import CODES, DATATYPES, DEFAULT_EOP
from typing import Union, List


class Payload():
    def __init__(self, data: Union[bytes, str, int] = b'',
                 dtype: str = None, length: int = None):
        self.dtype = self.get_dtype(dtype, data=data)
        self.length = self.get_length(length, data=data)
        self.data = self.get_data(data)
        self.encoded = self.get_encoded()

    def __call__(self):
        return self.encoded

    def get_dtype(self, dtype, data) -> str:
        if dtype:
            return dtype
        else:
            dtp = type(data)
            if dtp == str:
                return DATATYPES["str"]
            elif dtp == int:
                return DATATYPES["int"]
            elif dtp == float:
                return DATATYPES["float"]
            elif dtp == bytes:
                return DATATYPES["bytes"]
            else:
                # return DATATYPES["bytes"]
                return None

    def is_valid(self):
        a = self.length != None
        b = self.encoded != None
        return all([a, b])

    def get_length(self, length, data) -> int:
        if length:
            return length
        else:
            if data == None:
                data = b""
            adapter = {
                "B": lambda d: len(d),
                "S": lambda d: len(d),
                "I": lambda d: d.bit_length()//8+1,
                "F": lambda d: len(str(d).encode())
            }
            if self.dtype in adapter:
                return adapter[self.dtype](data)
            else:
                return 0

    def describe(self):
        return {
            "encoded": self.encoded,
            "length": self.length,
            "dtype": self.dtype
        }

    def get_data(self, data) -> Union[int, float, str, bytes]:
        if type(data) == bytes:
            if data != None:
                adapter = {
                    "B": lambda d: d,
                    "S": lambda d: d.decode(),
                    "I": lambda d: int.from_bytes(d, 'big'),
                    "F": lambda d: float(d)
                }
                return adapter[self.dtype](data)
            else:
                return b''
        else:
            if self.dtype is not None:
                return data
            else:
                return None

    def get_encoded(self) -> bytes:
        if type(self.data) == bytes:
            return self.data
        elif type(self.data) == str:
            return self.data.encode()
        elif type(self.data) == float:
            return str(self.data).encode()
        elif type(self.data) == int:
            return self.data.to_bytes(length=4, byteorder='big')
        else:
            return b''
