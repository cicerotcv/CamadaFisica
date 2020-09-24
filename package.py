# -*- coding: utf-8 -*-
from constants import CODES, DATATYPES, DEFAULT_EOP
from data_parser import Parser
from head import Head
from payload import Payload
from typing import Union, List


class Package():
    """
    Recebe uma sequência de bytes e decodifica em Head, Payload e End of Package 
    ou recebe dados suficientes para construir um Package.

    Atributos
    --------

    `head (Head):` Head com as características do Payload;

    `payload (Payload):` Payload que guarda os dados do pacote;

    `end_of_package (str):` End of Package que serve para validação de integridade;

    `encoded (bytes):` Pacote convertido em bytes;

    Métodos
    -----

    `is_valid:`  deve sempre retornar True;

    `is_handshake:` retorna True se o pacote for um handshake;

    `is_error:` retorna True se o pacote for uma notificação de erro;
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

        # --> atributos <-- #
        # self.head
        # self.payload
        # self.end_of_package
        # self.encoded

    def __call__(self) -> bytes:
        """Devolve a versão em bytes do pacote;
        Returns:

            bytes: b'DB\\x04\\x00\\x00\\x00\\x00\\x00\\x00\\x00ABCD1997'
        """
        return self.encoded

    def describe(self):
        return {
            "head": self.head.describe(),
            "payload": self.payload.describe(),
            "end_of_package":  self.end_of_package,
            "size": self.payload.length + 14,
            "encoded": self.encoded
        }

    def is_valid(self) -> bool:
        """Nunca deve retornar False;

        Returns:

            bool: Verifica se o pacote está legível. 
            Se o pacote contiver erros, ainda assim deve 
            ser convertido em um pacote de error (código "E")
            e se manter legível
        """
        a = self.head.is_valid()  # head
        b = self.payload.is_valid()  # payload
        c = self.end_of_package == DEFAULT_EOP  # end of package
        d = self.head.length == self.payload.length
        return all([a, b, c, d])

    def is_handshake(self) -> bool:
        """Verifica se o tipo do pacote é handshake (código "H")

        Returns:

            bool: True | False
        """
        return self.head.code == "H"

    def is_error(self) -> bool:
        """Verifica se o tipo do pacote é error (código "E")

        Returns:

            bool: True | False
        """
        return self.head.code == "E"

    def get_end_of_package(self) -> str:
        return DEFAULT_EOP

    def get_encoded(self) -> bytes:
        """Devolve a versão em bytes do pacote;
        Returns:

            bytes: b'DB\\x04\\x00\\x00\\x00\\x00\\x00\\x00\\x00ABCD1997'
        """
        return self.head() + self.payload() + self.end_of_package.encode()
