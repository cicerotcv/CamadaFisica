# -*- coding: utf-8 -*-
from constants import DEFAULT_EOP, get_code
from typing import Union, List


class Parser():
    """Conversor de bytes; `mode = "decoded" ou "encoded"`"""

    def __init__(self, data: bytes = None):
        self.data = data
        self.code = self.get_code()
        self.dtype = self.get_dtype()
        self.payload = self.get_payload()
        self.length = self.get_length()
        self.remaining = self.get_remaining()
        self.eop = self.get_eop()

    def get_code(self) -> str:
        """`D:default` `E:error` `H:handshake`"""
        try:
            code = self.data[:1].decode()
            return get_code(code)
        except:
            return "E"

    def get_dtype(self) -> str:
        """retorna `S:str` `F:float` `I:int` `B:bytes`"""
        if self.code != "E":
            datatype_code = self.data[1:2]
            return datatype_code.decode()
        else:
            return "B"

    def get_length(self) -> int:
        """retorna o tamanho do `payload`"""
        if self.code != "E":
            length_bytes = self.data[2:3]
            length = int.from_bytes(length_bytes, 'big')
            if length == get_length(self.payload):
                return length
            else:
                self.set_error()
        return 0

    def get_remaining(self) -> int:
        """retorna o número de pacotes restantes"""
        if self.code != "E":
            remaining = self.data[3:10]
            return int.from_bytes(remaining, 'big')
        else:
            return 0

    def get_payload(self) -> Union[int, str, bytes, float]:
        if self.code != "E":
            payload = self.data[10:].rstrip(DEFAULT_EOP.encode())
            if self.dtype == "I":
                return int.from_bytes(payload, byteorder='big')
            elif self.dtype == "S":
                return payload.decode()
            else:
                return payload
        else:
            return b""

    def get_eop(self) -> bytes:
        eop = self.data[-4:]
        if len(eop) and eop.decode() == DEFAULT_EOP:
            return eop.decode()
        else:
            self.set_error()
            return DEFAULT_EOP
    
    def set_error(self):
        self.data=b""
        self.code = "E"
        self.dtype = "B"
        self.payload = b""
        self.length = 0
        self.remaining = 0

def get_length(data: Union[int, str, bytes, float]) -> int:
    if type(data) == int:
        return data.bit_length()//8 + 1
    elif type(data) in [str, bytes]:
        return len(data)
    else:
        return 0
