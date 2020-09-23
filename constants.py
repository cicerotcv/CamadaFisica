CODES = {
    "default": "D",
    "error": "E",
    # "first": "F",
    "handshake": "H",
    # "last": "L"
}

DATATYPES = {
    "str": "S",
    "int": "I",
    "float": "F",
    "bytes": "B"
}
DEFAULT_EOP = "1997"

def get_code(code):
    if code in CODES.values():
        return code
    if code in CODES.keys():
        return CODES[code]
    else:
        return "E"