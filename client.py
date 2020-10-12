# coding: utf-8
from enlace import enlace
from camfis_utils import Logger
from package import Package, Handshake, Idle, Default, Confirmation, Timeout, Error
from data_queue import Splitter, PackageQueue
import time
import traceback

class Client(enlace):
    def __init__(self, comName, filename=""):
        super(Client, self).__init__(comName)
        self.log = Logger("CLIENT", filename).log
        self.id_arquivo = None
        self.file = b""
        self.package_queue: PackageQueue = None
        self.task_completed = False
        self.force_error = False
        self.attempts = 5

    def load_file(self, filename):
        try:
            file = open(filename, 'rb')
            self.file = file.read()
            file.close()

            splitter = Splitter(self.file)
            self.package_queue = PackageQueue(splitter.splitted)
            self.log(f"Nº total de pacotes: {self.package_queue.length}")
        except Exception as e:
            self.log("Erro ao carregar arquivo;")
            print(e)
            raise Exception

    def server_is_idle(self, attempts) -> bool:
        """Deals with first contact between client and server;"""
        received, timeout = self.getData(14)
        self.deal_with_timeout(timeout, attempts=attempts)
        if not timeout:
            response = Package(encoded=received)
            if response.is_idle():
                self.log(
                    f"[RECEB][TIPO {response.head.type}][SIZE {response.size}]")
                return True
            else:
                return False
        else:
            return False

    def handle_response(self):
        """Deals with response received from server"""
        received, timeout = self.getData(14)
        self.deal_with_timeout(timeout)
        response = Package(encoded=received)
        if response.is_confirmation():
            self.log(
                f"[RECEB][TIPO {response.head.type}][SIZE {response.size}B]")
            if self.package_queue.has_next():
                if self.package_queue.current == 4 and self.force_error:
                    self.send_again(2)
                    self.force_error = False
                else:
                    self.send_next()
            else:
                self.task_completed = True
        elif response.is_error():
            self.log(
                f"[RECEB][TIPO {response.head.type}][REENVIAR {response.last_received + 1}]")
            self.send_again(response.last_received+1)

        elif response.is_timeout():
            self.log("Timeout recebido :(")

    def send_next(self):
        package = self.package_queue.get_next()
        self.log(
            f"[ENVIO][TIPO {package.head.type}][SIZE {package.size}B]"
            f"[PACOTE #{package.head.current_package:02d}]"
            f"[TOTAL {package.head.total_packages}][{package.head.remainder}]")
        self.sendData(package.encoded)

    def send_again(self, n):
        package = self.package_queue.get_nth(n)
        self.log(
            f"[ENVIO][TIPO {package.head.type}][SIZE {package.size}B]"
            f"[PACOTE #{package.head.current_package:02d}]"
            f"[TOTAL {package.head.total_packages}][{package.head.remainder}]")
        self.sendData(package.encoded)

    def deal_with_timeout(self, timeout, attempts=0):
        if timeout and self.attempts >= attempts:
            self.sendData(Timeout(1, 2)())
            raise TimeoutError

    def send_handshake(self):
        package = Handshake(1, 2, 0, self.package_queue.length)
        self.log(
            f"[ENVIO][TIPO {package.head.type}][SIZE {package.size}B][TOTAL {package.head.total_packages}]")
        self.sendData(package.encoded)


if __name__ == "__main__":
    client = Client('com1', "client5.txt")
    client.log("Client construído;")

    client.log("Carregando arquivo;")
    client.load_file("qrcode.png")
    try:
        # habilitar o client
        client.enable()

        # estabelecer conexão
        server_idle = False
        attempts = 1
        while not server_idle and attempts < 5:
            client.log(f"Tentativa #{attempts}")
            # enviando handshake
            client.send_handshake()
            # client.handle_response()
            server_idle = client.server_is_idle(attempts)
            attempts += 1

        task_completed = False
        client.send_next()
        while not task_completed:
            client.handle_response()
            task_completed = client.task_completed

    except TimeoutError:
        client.log("Tempo de espera excedido;")
    except Exception as e:
        traceback.print_exc()
        client.log("Erro ao processar instrução;")
    finally:
        client.log("Comunicação encerrada.")
        client.disable()
