# coding: utf-8
from enlace import enlace
from camfis_utils import Logger
from package import Package, Handshake, Idle, Default, Confirmation, Timeout, Error


class Server(enlace):
    def __init__(self, comName):
        super(Server, self).__init__(comName)
        self.log = Logger("SERVER").log
        self.id_arquivo = None
        # self.rx
        # self.tx
        # self.fisica

    def await_handshake(self):
        """Server awaits for 14 bytes which match a handshake pattern"""
        handshake_received = False
        data, timeout = self.getData(14)
        if timeout:
            response = Timeout(1, 2)
            self.sendData(response())
            raise TimeoutError
        else:
            received = Package(encoded=data)
            if received.is_handshake():
                self.id_arquivo = received.id_arquivo
            else:
                raise Exception

    def await_default(self):
        """Server awaits for a stable amount of bytes white matches a default type 3 message"""
        pass


if __name__ == "__main__":
    server = Server("com2")
    server.log("Comunicação iniciada")

    try:
        # habilitar o server
        server.enable()

        # aguardar handshake
        server.log("Aguardando Handshake;")
        server.await_handshake()

        done = False
        while not done:
            # aguardando pacotes
            server.await_default()

    except TimeoutError:
        server.log("Tempo de espera excedido;")

    except Exception as e:
        server.log("Erro ao processar instrução;")

    finally:
        server.log("Comunicação encerrada.")
        server.disable()
