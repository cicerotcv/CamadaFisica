CODES = {
    "default": "D",
    "error": "E",
    "handshake": "H",
}

DATATYPES = {
    "str": "S",
    "int": "I",
    "float": "F",
    "bytes": "B"
}

DEFAULT_EOP = "1997"
PACKAGE_SIZE = 128
HEAD_SIZE = 10
END_OF_PACKAGE_SIZE = 4
PAYLOAD_SIZE = PACKAGE_SIZE - (HEAD_SIZE + END_OF_PACKAGE_SIZE)


def get_code(code:str) -> str:
    """Devolve o código no formato correto

    Args:
        code (str): Código que pode ser ["E", "error", "H", "handshake", "D", "default"]

    Returns:
        str: ["E", "H", "D"]
    """
    if code in CODES.values():
        return code
    if code in CODES.keys():
        return CODES[code]
    else:
        return "E"

def get_length(data) -> int:
    """[summary]

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