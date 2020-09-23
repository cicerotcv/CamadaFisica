# -*- coding: utf-8 -*-
from constants import CODES, DATATYPES, DEFAULT_EOP
from data_parser import Parser
from head import Head
from payload import Payload
from typing import Union, List


class Package():
    """
    Recebe uma sequência e se encarrega de 
    adicionar um `head` e um `end of package`
    """

    def __init__(self, content: Union[bytes, str, int] = b'',
                 code: str = "default", remaining: int = 0, encoded: bytes = None):
        if encoded:
            self.parser = Parser(encoded)
            self.head = Head(code=self.parser.code,
                             dtype=self.parser.dtype,
                             length=self.parser.length,
                             remaining=self.parser.remaining)
            self.payload = Payload(
                data=self.parser.payload,
                dtype=self.parser.dtype,
                length=self.parser.length)
            self.end_of_package = self.parser.eop
        else:
            self.payload = Payload(content)
            self.head = Head(code=code, dtype=self.payload.dtype,
                             length=self.payload.length, remaining=remaining)
            self.end_of_package = self.get_end_of_package()
        self.encoded = self.get_encoded()

        # self.head
        # self.payload
        # self.end_of_package
        # self.encoded

    def __call__(self):
        return self.encoded

    def describe(self):
        return {
            "head": self.head.describe(),
            "payload": self.payload.describe(),
            "end_of_package":  self.end_of_package,
            "size": self.payload.length + 14,
            "encoded": self.encoded
        }

    def is_valid(self):
        a = self.head.is_valid()  # head
        b = self.payload.is_valid()  # payload
        c = self.end_of_package == DEFAULT_EOP  # end of package
        d = self.head.length == self.payload.length
        # print(f"{self.head.length} == {self.payload.length} ")
        return all([a, b, c, d])

    def is_handshake(self):
        return self.head.code == "H"

    def is_error(self):
        return self.head.code == "E"

    def get_end_of_package(self) -> str:
        return DEFAULT_EOP

    def get_encoded(self) -> bytes:
        """
        Combina `head` com `payload` e `end of package` para gerar 
        a mensagem do pacote.
        """
        return self.head() + self.payload() + self.end_of_package.encode()
