# -*- coding: utf-8 -*-

from typing import List, Union
from camfis_utils import CODES

"""
h0: tipo da mensagem
    handshake: 1
    idle: 2
    default: 3  deve conter o número do pacote enviado
    confirmation: 4  # deve conter o número do último pacote recebido
    timeout: 5 
    error: 6  deve enviar quando receber tipo 3 inválida
h1: id sensor int
h2: id server int
h3: número total de pacotes no arquivo
h4: número do pacote sendo enviado
h5: handshake => id do arquivo (int) || default => tamanho do payload
h6: pacote solicitado para recomeço quando há erro no envio
h7: último pacote recebido
h8-h9: CRC

"""


class Head():
    """Classe que constrói, processa e valida um Head. 
    Embora não precise ser instanciada diretamente, é utilizada
    internamente ao construir um Package.
    """

    def __init__(self, tipo: int, id_sensor: int, id_server: int, total_packages: int,
                 current_package: int, h5: int, h6: int, last_received: int, remainder: bytes):
        self.type = tipo
        self.id_sensor = id_sensor
        self.id_server = id_server
        self.total_packages = total_packages
        self.current_package = current_package
        self.h5 = h5
        self.h6 = h6
        self.last_received = last_received
        self.remainder = remainder  # 2 bytes

    def __call__(self):
        return self.encode()

    def is_valid(self) -> bool:
        return self.type in list(CODES.keys()) + list(CODES.values())

    def encode(self) -> bytes:
        a = int.to_bytes(self.type, 1, 'big')
        b = int.to_bytes(self.id_sensor, 1, 'big')
        c = int.to_bytes(self.id_server, 1, 'big')
        d = int.to_bytes(self.total_packages, 1, 'big')
        e = int.to_bytes(self.current_package, 1, 'big')
        f = int.to_bytes(self.h5, 1, 'big')
        g = int.to_bytes(self.h6, 1, 'big')
        h = int.to_bytes(self.last_received, 1, 'big')
        encoded = a + b + c + d + e + f + g + h
        return encoded + self.remainder

    def is_handshake(self):
        return self.type == 1

    def is_idle(self):
        return self.type == 2

    def is_default(self):
        return self.type == 3

    def is_confirmation(self):
        return self.type == 4

    def is_timeout(self):
        return self.type == 5

    def is_error(self):
        return self.type == 6


if __name__ == "__main__":
    head = Head(1, 2, 3, 4, 5, 6, 7, 8, b'\x00\x00')
    print(head.encode())
