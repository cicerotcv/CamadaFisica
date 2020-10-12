# coding: utf-8
from enlace import enlace
from camfis_utils import Logger
from package import Package, Handshake, Idle, Default, Confirmation, Timeout, Error
from data_queue import Storage, Assembler
import time
import traceback


class Server(enlace):
    def __init__(self, comName, filename=""):
        super(Server, self).__init__(comName)
        self.log = Logger("SERVER", filename).log
        self.id_arquivo = None
        self.expected = 1
        self.total = None
        self.storage = Storage()
        self.attempts = 5

    def receive_handshake(self,attempts):
        """Server awaits for 14 bytes which match a handshake pattern;"""
        data, timeout = self.getData(14)
        self.deal_with_timeout(timeout, attempts)

        if not timeout:
            received = Package(encoded=data)
            if received.is_handshake():
                self.process_handshake(received)
                idle = Idle(1, 2)
                self.log(f"[ENVIO][TIPO {idle.head.type}][SIZE {idle.size}]")
                self.sendData(idle.encoded)
                return received.is_handshake()
            else:
                return False
        return False

    def process_handshake(self, handshake):
        self.id_arquivo = handshake.id_arquivo
        self.total = handshake.head.total_packages

    def await_default(self):
        """Server awaits for a stable amount of bytes white matches a default type 3 message;"""
        self.await_rx_buffer()
        data = self.getAllData()
        package = Package(encoded=data)
        # verifica se há erro ou fora de ordem:
        if (not package.is_valid()) or (package.head.current_package != self.expected):
            self.log(
                f"[RECEB][TIPO {package.head.type}][SIZE {package.size}B]"
                f"[PACOTE #{package.head.current_package:02d}]"
                f"[TOTAL {package.head.total_packages}][{package.head.remainder}]")
            error = Error(1, 2, self.expected-1)
            self.log(
                f"[ENVIO][TIPO {error.head.type}][REENVIAR {self.expected}]")
            self.sendData(error.encoded)
        # caso o pacote seja válido:
        else:
            self.storage.insert(package)
            self.log(
                f"[RECEB][TIPO {package.head.type}][SIZE {package.size}B]"
                f"[PACOTE #{package.head.current_package:02d}]"
                f"[TOTAL {package.head.total_packages}][{package.head.remainder}]")
            self.expected = self.expected + 1
            self.send_confirmation()

    def send_confirmation(self):
        """Server sends a confirmation-like bytearray to client;"""
        confirmation = Confirmation(1, 2)
        self.log(
            f"[ENVIO][TIPO {confirmation.head.type}][SIZE {confirmation.size}B]")
        self.sendData(confirmation.encoded)

    def send_timeout(self):
        timeout = Timeout(1, 2)
        self.sendData(timeout.encoded)

    def await_rx_buffer(self) -> bytes:
        """Server awaits for its Rx Buffer to become stable;"""
        bufferLen = self.rx.getBufferLen()
        now = time.time
        before = now()
        while (now() - before < 5):
            if 0 < self.rx.getBufferLen() == bufferLen:
                return
            else:
                bufferLen = self.rx.getBufferLen()
            time.sleep(0.1)
        raise TimeoutError

    def deal_with_timeout(self, timeout, attempts):
        if timeout and (self.attempts <= attempts):
            self.sendData(Timeout(1, 2)())
            raise TimeoutError

    def getAllData(self) -> bytes:
        """Returns all data stored in Rx Buffer"""
        return self.rx.getAllBuffer()

    def is_done(self):
        return self.total == self.expected - 1


if __name__ == "__main__":
    server = Server("com2", "server5.txt")
    server.log("Comunicação iniciada")

    try:
        # habilitar o server
        server.enable()

        # aguardar handshake (estabelecer conexão)
        attempts = 1
        handshake_received = False
        while (not handshake_received) and attempts < 5:
            server.log(f"Tentativa #{attempts}")
            handshake_received = server.receive_handshake(attempts)
            attempts += 1

        done = False
        # aguardar o recebimento e lidar com possíveis erros
        server.log("Aguardando pacotes;") 
        while not done:
            # aguardando pacotes
            server.await_default()  # contém a pipeline para lidar com erros

            done = server.is_done()
        # total de bytes recebidos
        server.log(f'{server.storage.size} bytes recebidos;')

        assembler = Assembler(server.storage)
        assembler.write(f"ID{server.id_arquivo}.png")

        server.log(f"Arquivo salvo em ID{server.id_arquivo}.png")

    except TimeoutError:
        server.log("Tempo de espera excedido;")
        server.send_timeout()

    except Exception as e:
        server.log("Erro ao processar instrução;")
        traceback.print_exc()

    finally:
        server.log("Comunicação encerrada.")
        server.disable()
