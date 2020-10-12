# coding: utf-8
import time
from datetime import datetime
import arrow
CODES = {
    "handshake": 1,
    "idle": 2,
    "default": 3,
    "confirmation": 4,
    "timeout": 5,
    "error": 6
}

EOP = b'\xff\x00\xff\x00'  # end of package esperado
PAYLOAD_SIZE = 114


class Logger():
    def __init__(self, name: str, filename: str = ""):
        self.name = name
        self.filename = filename

    def log(self, text):
        timestamp = datetime.strftime(
            datetime.fromtimestamp(time.time()), "%Y/%m/%d %H:%M:%S.%f")
        print(f'[{self.name}][{timestamp}] {text}')
        if self.filename.endswith(".txt"):
            with open(self.filename, 'a+', encoding='utf-8') as stdout:
                print(f'[{self.name}][{timestamp}] {text}', file=stdout)


def get_length(data) -> int:
    """Devolve a quantidade de bytes necessária para escrever
    um número, uma string ou uma lista de bytes;

    Args:
        data ([int, str, bytes]): argumento que terá seu "tamanho" medido em bytes

    Returns:
        int: quantidade de bytes necessárias para escrever "data" em bytes
    """
    if type(data) == int:
        return data.bit_length()//8 + 1
    elif type(data) in [str, bytes]:
        return len(data)
    else:
        return 0


def bytes_to_bin(data: bytes) -> str:
    in_bytes = int.from_bytes(data, 'big')
    binary = bin(in_bytes)[2:]
    return binary


def bytes_to_int(bts: bytes) -> int:
    return int.from_bytes(bts, 'big')


def int_to_bytes(nmb: int, length: int = 1) -> bytes:
    return int.to_bytes(nmb, length, 'big')

# adaptado de www.geeksforgeeks.org/cyclic-redundancy-check-python/


def xor(a, b):
    # initialize result
    result = []

    # Traverse all bits, if bits are
    # same, then XOR is 0, else 1
    for i in range(1, len(b)):
        if a[i] == b[i]:
            result.append('0')
        else:
            result.append('1')

    return ''.join(result)


def mod2div(divident, divisor):
    # Performs Modulo-2 division

    # Number of bits to be XORed at a time.
    pick = len(divisor)

    # Slicing the divident to appropriate
    # length for particular step
    tmp = divident[0: pick]

    while pick < len(divident):

        if tmp[0] == '1':

            # replace the divident by the result
            # of XOR and pull 1 bit down
            tmp = xor(divisor, tmp) + divident[pick]

        else:  # If leftmost bit is '0'
            # If the leftmost bit of the dividend (or the
            # part used in each step) is 0, the step cannot
            # use the regular divisor; we need to use an
            # all-0s divisor.
            tmp = xor('0'*pick, tmp) + divident[pick]

        # increment pick to move further
        pick += 1

    # For the last n bits, we have to carry it out
    # normally as increased value of pick will cause
    # Index Out of Bounds.
    if tmp[0] == '1':
        tmp = xor(divisor, tmp)
    else:
        tmp = xor('0'*pick, tmp)

    checkword = tmp
    return checkword


def encodeData(data, key):
    # Function used at the sender side to encode
    # data by appending remainder of modular division
    # at the end of data.

    l_key = len(key)

    # Appends n-1 zeroes at end of data
    appended_data = data + '0'*(l_key-1)
    remainder = mod2div(appended_data, key)

    # Append remainder in the original data
    codeword = remainder
    return codeword


def encode(message: bytes, poly: bytes = b"\xE2\xA5") -> int:
    key = bytes_to_bin(poly)
    message = bytes_to_bin(message)
    return encodeData(message, key)


def get_remainder(message: bytes, poly: bytes = b'\xE2\xA5') -> bytes:
    remainder = encode(message)
    return int.to_bytes(int(remainder, 2), 2, 'big')


if __name__ == "__main__":
    mensagem = b'\x45\x00\x00\x3c\x00\x00\x00\x00\x40\x11\x00\x00\xc0\xa8\x2b\xc3\x08\x08\x08\x08\x11'
    # mensagem = b'\x45\x32'
    # remainder = encode(mensagem)
    # print(f'remainder: {remainder}')
    # hex_remainder = int.to_bytes(int(remainder, 2), 2, 'big')
    # print(f'hex remainder: {hex_remainder}')

    remainder = get_remainder(mensagem)
    print(f"Resto: {remainder}")

    # logger = Logger("Server")
    # logger("Hello world")
    timestamp = datetime.strftime(
        datetime.fromtimestamp(time.time()), "%Y/%m/%d %H-%M-%S.%f")

    print(timestamp)
