# -*- coding: utf-8 -*-

from typing import List, Union

from constants import CODES, DATATYPES, DEFAULT_EOP, get_code


class Head():
    """Classe que constrói, processa e valida um Head. 
    Embora não precise ser instanciada diretamente, é utilizada
    internamente ao construir um Package.
    """

    def __init__(self, code: str = "default", dtype: str = "bytes", length: int = 0,
                 remaining: int = 0):
        """

        Args:
            code (str, optional): Código que classifica o Package. Defaults to "default".
            dtype (str, optional): Tipo de dado no qual o payload pode ser convertido. Defaults to "bytes".
            length (int, optional): Comprimento em bytes do Payload. Defaults to 0.
            remaining (int, optional): Quantidade restante de pacotes (packages) a serem recebidos. Defaults to 0.
        """

        self.code: str = get_code(code)
        self.dtype: str = self.get_dtype(dtype)
        self.length: int = length
        self.remaining: int = remaining
        self.encoded = self.get_encoded()
        self.decoded = self.get_decoded()

    def __call__(self):
        return self.encoded

    def describe(self) -> dict:
        """Devolve um dicionário contendo todos os atributos do Head

        Returns:
            dict: 
            exemplo = {
                "code": "D", 
                "dtype": "B",
                "length": 9, 
                "remaining": 11, 
                "encoded": b"DB\\x09\\x00\\x00\\x00\\x00\\x00\\x00\\x0B", 
                "decoded": ("D", "B", 9, 11)
            }
        """
        return {
            "code": self.code,
            "dtype": self.dtype,
            "length": self.length,
            "remaining": self.remaining,
            "encoded": self.encoded,
            "decoded": self.decoded
        }

    def get_encoded(self) -> bytes:
        return self.code.encode() \
            + self.dtype.encode() \
            + self.length.to_bytes(1, 'big') \
            + self.remaining.to_bytes(7, 'big')

    def get_decoded(self) -> bytes:
        """(code, length, remaining)"""
        return (self.code, self.dtype, self.length, self.remaining)

    def is_valid(self):
        if self.code not in list(CODES.values()) + list(CODES.keys()):
            print(f"[HEAD] code not in CODES")
            self.code = "E"
            return False
        if self.dtype not in list(DATATYPES.keys()) + list(DATATYPES.values()):
            print(f"[HEAD] dtype not in DATATYPES")
            self.code = "E"
            return False
        if not 0 <= self.length < 128:
            self.code = "E"
            return False
        if not 0 <= self.remaining < 2**56:
            self.code = "E"
            return False
        return True

    def get_dtype(self, dtype) -> object:
        if dtype in DATATYPES.keys():
            return DATATYPES[dtype]
        elif dtype in DATATYPES.values():
            return dtype
        else:
            return "B"
