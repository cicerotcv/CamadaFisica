# -*- coding: utf-8 -*-
from typing import Union, List
from head import Head
from payload import Payload
from end_of_package import EndOfPackage
from adapter import Adapter
from camfis_utils import get_remainder, EOP


class Package():
    # tipo: int, id_sensor: int, id_server: int, total_packages: int,
    #  current_package: int, h5: int, h6: int, last_received: int, remainder: bytes
    def __init__(self, message: bytes = b'', type: int = 0, id_sensor: int = 1,
                 id_server: int = 2, total_packages: int = 0, current_package: int = 0,
                 h5: int = 0, h6: int = 0, last_received: int = 0,
                 encoded: bytes = None):
        if encoded != None:
            adapter = Adapter(encoded)
            self.head = adapter.head
            self.payload = adapter.payload
            self.end_of_package = adapter.end_of_package
        else:
            self.head = self.create_head(type, id_sensor, id_server,
                                         total_packages, current_package, h5,
                                         h6, last_received, message)
            self.payload = Payload(message)
            self.end_of_package = EndOfPackage().eop

    def __call__(self):
        head = self.head()
        payload = self.payload()
        eop = self.end_of_package
        return head + payload + eop

    def is_valid(self):
        """Must be used by receiver"""
        a = self.head.is_valid()
        b = self.payload.is_valid()
        c = self.end_of_package.is_valid()
        if self.is_default():
            d = get_remainder(self.payload.message) == self.head.remainder
        else:
            d = True
        return all([a, b, c, d])

    def is_handshake(self):
        """Tipo 1"""
        boolean = self.head.is_handshake()
        if boolean:
            self.id_arquivo: self.head.h5
        return boolean

    def is_idle(self):
        """Tipo 2"""
        return self.head.is_idle()

    def is_default(self):
        """Tipo 3"""
        return self.head.is_default()

    def is_confirmation(self):
        """Tipo 4"""
        return self.head.is_confirmation()

    def is_timeout(self):
        """Tipo 5"""
        return self.head.is_timeout()

    def is_error(self):
        """Tipo 6"""
        return self.head.is_error()

    def create_head(self, type, id_sensor, id_server,
                    total_packages, current_package, h5, h6, last_received, message):
        if type == 3:
            h5 = len(message)
            h6 = 0
            remainder = get_remainder(message)
        elif type == 6:
            h5 = 0
            remainder = b'\x00\x00'
        else:
            remainder = b'\x00\x00'

        head = Head(type, id_sensor, id_server, total_packages,
                    current_package, h5, h6, last_received, remainder)
        return head


class Handshake(Package):
    def __init__(self, id_sensor, id_server, id_arquivo):
        super(Handshake, self).__init__(type=1, id_sensor=id_sensor,
                                        id_server=id_server, h5=id_arquivo)


class Idle(Package):
    def __init__(self, id_sensor, id_server):
        super(Idle, self).__init__(
            type=2, id_sensor=id_sensor, id_server=id_server)


class Default(Package):
    def __init__(self, message, id_sensor, id_server, current_package, total_packages):
        super(Default, self).__init__(message=message, type=3, id_sensor=id_sensor,
                                      id_server=id_server, total_packages=total_packages,
                                      current_package=current_package)


class Confirmation(Package):
    def __init__(self, id_sensor, id_server):
        super(Confirmation, self).__init__(
            type=4, id_sensor=id_sensor, id_server=id_server)


class Timeout(Package):
    def __init__(self, id_sensor, id_server):
        super(Timeout, self).__init__(
            type=5, id_sensor=id_sensor, id_server=id_server)


class Error(Package):
    def __init__(self, id_sensor, id_server, last_received):
        super(Handshake, self).__init__(type=6, id_sensor=id_sensor,
                                        id_server=id_server, h6=last_received)


if __name__ == "__main__":
    handshake = Handshake(1, 2, 3)
    print(handshake.is_handshake())

    print(handshake())
    data = Package(encoded=handshake())
    print(data())
