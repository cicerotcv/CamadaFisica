# -*- coding: utf-8 -*-
from typing import Union, List
from head import Head
from payload import Payload
from end_of_package import EndOfPackage
from camfis_utils import bytes_to_int, EOP


class Adapter():
    """Conversor de bytes;"""

    def __init__(self, data: bytes = None):
        if self.is_valid(data):
            self.head = self.get_head(data)
            self.payload = self.get_payload(data)
            self.end_of_package = EOP
        else:
            self.head = Head(0, 0, 0, 0, 0,
                             0, 0, 0, b'\x00\x00')
            self.payload = Payload(b'')
            self.end_of_package = b'\x00\x00\x00\x00'

    def get_head(self, data) -> Head:
        return Head(
            data[0],  # h0
            data[1],  # h1
            data[2],  # h2
            data[3],  # h3
            data[4],  # h4
            data[5],  # h5 id_arquivo || tamanho_payload
            data[6],  # h6 package_number if error
            data[7],  # h7
            data[8:10]              # h8, h9
        )

    def get_payload(self, data) -> Payload:
        return Payload(data[10:-4])

    def is_valid(self, data) -> bool:
        # data[0]      | tipo da mensagem
        # data[1] != 0 | id_sensor
        # data[2] != 0 | id_server
        # data[3]      | total number of packages
        # data[4]      | current package number
        # data[5]      | h0 = 1 => id_arquivo; h0 = 3 => len(payload)
        # g = 0 <= f <= e
        return all([
            14 <= len(data) <= 128,  # verifica se o tamanho do pacote é válido
            1 <= data[0] <= 6,       # verifica se o tipo da mensagem existe
            data[-4:] == EOP,        # verifica se o eop é válido
        ])


if __name__ == "__main__":
    # b'\x01\x02\x03\x04\x05\x06\x07\x08\x00\x00'
    message = b'\x01\x02\x03\x04\x05\x06\x07\x08\x00\x00' + EOP
    print(message)
    parser = Adapter(message)
    print(parser.head())
