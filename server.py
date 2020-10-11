# coding: utf-8
# chcp 65001
from enlace import enlace
from camfis_utils import Logger
from package import Package, Handshake, Idle, Default, Confirmation, Timeout, Error
from data_queue import Storage, Assembler


class Server(enlace):
    def __init__(self, comName):
        super(Server, self).__init__(comName)
        self.log = Logger("SERVER", "server1.txt").log
        self.id_arquivo = None
        self.expects_for = 0

        self.storage = Storage()

        # self.rx
        # self.tx
        # self.fisica

    def await_handshake(self):
        """Server awaits for 14 bytes which match a handshake pattern"""
        handshake_received = False
        data, timeout = self.getData(14)
        self.deal_with_timeout(timeout)

        received = Package(encoded=data)
        if received.is_handshake():
            self.id_arquivo = received.id_arquivo
        else:
            raise Exception

    def await_default(self):
        """Server awaits for a stable amount of bytes white matches a default type 3 message"""
        pass

    def send_confirmation(self):
        """Server sends a confirmation-like bytearray to client"""
        pass

    def deal_with_timeout(self, timeout):
        if timeout:
            response = Timeout(1, 2)
            self.sendData(response())
            raise TimeoutError


if __name__ == "__main__":
    server = Server("com2")
    server.log("Comunicação iniciada")

    try:
        # habilitar o server
        server.enable()

        # aguardar handshake
        server.log("Aguardando Handshake;")
        server.await_handshaike()

        done = False
        # aguardar o recebimento e lidar com possíveis erros
        while not done:
            # aguardando pacotes
            server.await_default()  #q contém a pipeline para lidar com erros
        # confirmar o recebimento
        pass

    except TimeoutError:
        server.log("Tempo de espera excedido;")

    except Exception as e:
        server.log("Erro ao processar instrução;")
        print(f'\t{e}')

    finally:
        server.log("Comunicação encerrada.")
        server.disable()
