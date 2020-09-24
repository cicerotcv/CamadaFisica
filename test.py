import unittest

from constants import DEFAULT_EOP
from data_parser import Parser
from data_queue import Splitter, PackageQueue
from head import Head
from package import Package
from payload import Payload

STR_ENCODED = b'DS\x04\x00\x00\x00\x00\x00\x00\x00ABCD1997'
INT_ENCODED = b'DI\x02\x00\x00\x00\x00\x00\x01\x00\x01\x011997'
BYTES_ENCODED = b'DB\x04\x00\x00\x00\x00\x00\x00\x00ABCD1997'
ERROR_ENCODED = b"EB\x00\x00\x00\x00\x00\x00\x00\x001997"
CORRUPTED_STREAM = b'\xfffff23fafafa'
HANDSHAKE_ENCODED = b"HB\x00\x00\x00\x00\x00\x00\x00\x001997"

file = open('qrcode.png', 'rb')
IMAGE = file.read()
file.close()


class TestParser(unittest.TestCase):
    def testParseBytesToStr(self):
        # b'DS\x04\x00\x00\x00\x00\x00\x00\x00ABCD1997'
        parser = Parser(data=STR_ENCODED)
        parser_test_function(self, parser=parser, code="D", dtype="S",
                             length=4, payload="ABCD", remaining=0)

        head = Head(code=parser.code, dtype=parser.dtype,
                    length=parser.length, remaining=parser.remaining)
        head_test_function(self, head=head, code="D",
                           dtype="S", length=4, remaining=0)

        payload = Payload(data=parser.payload,
                          dtype=parser.dtype, length=parser.length)
        payload_test_function(self, payload=payload,
                              data="ABCD", dtype="S", length=4)

    def testParseBytesToInt(self):
        parser = Parser(INT_ENCODED)
        parser_test_function(self, parser=parser, code="D", dtype="I",
                             length=2, payload=257, remaining=256)

        head = Head(code=parser.code, dtype=parser.dtype,
                    length=parser.length, remaining=parser.remaining)
        head_test_function(self, head=head, code="D",
                           dtype="I", length=2, remaining=256)

        payload = Payload(data=parser.payload,
                          dtype=parser.dtype, length=parser.length)
        payload_test_function(self, payload=payload,
                              data=257, dtype="I", length=2)

    def testParseBytesToBytes(self):
        # b'DB\x04\x00\x00\x00\x00\x00\x00\x00ABCD1997'
        parser = Parser(BYTES_ENCODED)
        parser_test_function(self, parser=parser, code="D", dtype="B",
                             length=4, payload=b'ABCD', remaining=0)

        head = Head(code=parser.code, dtype=parser.dtype,
                    length=parser.length, remaining=parser.remaining)
        head_test_function(self, head=head, code="D",
                           dtype="B", length=4, remaining=0)

        payload = Payload(data=parser.payload,
                          dtype=parser.dtype, length=parser.length)
        payload_test_function(self, payload=payload,
                              data=b'ABCD', dtype="B", length=4)

    def testParseBytesToError(self):
        parser = Parser(ERROR_ENCODED)
        parser_test_function(self, parser=parser, code="E", dtype="B",
                             length=0, payload=b"", remaining=0)
        head = Head(code=parser.code, dtype=parser.dtype,
                    length=parser.length, remaining=parser.remaining)
        head_test_function(self, head, "E", "B", 0, 0,
                           b'EB\00\00\00\00\00\00\00\00')

    def testParseCorruptedStreamToBytes(self):
        parser = Parser(CORRUPTED_STREAM)
        parser_test_function(self, parser=parser, code="E", dtype="B",
                             length=0, payload=b"", remaining=0)
        head = Head(code=parser.code, dtype=parser.dtype,
                    length=parser.length, remaining=parser.remaining)
        head_test_function(self, head, "E", "B", 0, 0,
                           b'EB\00\00\00\00\00\00\00\00')

    def testParseHandshakeToBytes(self):
        parser = Parser(HANDSHAKE_ENCODED)
        parser_test_function(self, parser=parser, code="H", dtype="B",
                             length=0, payload=b"", remaining=0)
        head = Head(code=parser.code, dtype=parser.dtype,
                    length=parser.length, remaining=parser.remaining)
        head_test_function(self, head=head, code="H",
                           dtype="B", length=0, remaining=0)
        payload = Payload(data=parser.payload,
                          dtype=parser.dtype, length=parser.length)
        payload_test_function(self, payload=payload,
                              data=b"", dtype="B", length=0)


class TestHead(unittest.TestCase):
    def testCreateDefaultHead(self):
        head = Head()
        head_test_function(self, head, "D", "B", 0, 0,
                           b"DB\x00\x00\x00\x00\x00\x00\x00\x00")
        self.assertEqual(head.decoded, ("D", "B", 0, 0))

    def testCreateHandshakeHead(self):
        head = Head(code='handshake')
        head_test_function(self, head, "H", "B", 0, 0,
                           b"HB\x00\x00\x00\x00\x00\x00\x00\x00")
        self.assertEqual(head.decoded, ("H", "B", 0, 0))

    def testCreateErrorHead(self):
        head = Head(code='codigo_inexistente', dtype=float)
        head_test_function(self, head, "E", "B", 0, 0,
                           b"EB\x00\x00\x00\x00\x00\x00\x00\x00")
        self.assertEqual(head.decoded, ("E", "B", 0, 0))


class TestPayload(unittest.TestCase):
    def testCreatePayloadFromInt(self):
        payload = Payload(data=10)
        payload_test_function(self, payload, 10, "I", 1)

    def testCreatePayloadFromStr(self):
        payload = Payload(data="Carro")
        payload_test_function(self, payload, "Carro", "S", 5)

    def testCreatePayloadFromBytes(self):
        payload = Payload(data=b'ABCD')
        payload_test_function(self, payload, b"ABCD", "B", 4)

    def testCreatePayloadFromSomethingElse(self):
        something_else = {"something": "else"}
        payload = Payload(data=something_else)
        payload_test_function(self, payload, None, None, 0, b"")


class TestPackage(unittest.TestCase):
    def testCreatePackageFromInt(self):
        package = Package(content=3, code="D", remaining=23)
        package_test_function(self, package, 3, "D", "I", 1, 23)
        self.assertFalse(package.is_handshake())
        self.assertFalse(package.is_error())

    def testParseIntEncodedToPackage(self):
        package = Package(encoded=INT_ENCODED)
        package_test_function(self, package, 257, "D", "I", 2, 256)
        self.assertFalse(package.is_handshake())
        self.assertFalse(package.is_error())

    def testCreatePackageFromStr(self):
        package = Package(content="hello_world", code="default", remaining=7)
        package_test_function(self, package, "hello_world", "D", "S", 11, 7)
        self.assertFalse(package.is_handshake())
        self.assertFalse(package.is_error())

    def testParseStrEncodedToPackage(self):
        # b'DS\x04\x00\x00\x00\x00\x00\x00\x00ABCD1997'
        package = Package(encoded=STR_ENCODED)
        package_test_function(self, package, "ABCD", "D", "S", 4, 0)
        self.assertFalse(package.is_handshake())
        self.assertFalse(package.is_error())

    def testCreatePackageFromBytes(self):
        package = Package(content=b'hello_world', code="D", remaining=9)
        package_test_function(self, package, b"hello_world", "D", "B", 11, 9)
        self.assertFalse(package.is_handshake())
        self.assertFalse(package.is_error())

    def testParseBytesToPackage(self):
        # Package's payload argument is given a encoded package of bytes
        # b'DB\x04\x00\x00\x00\x00\x00\x00\x00ABCD1997'
        package = Package(encoded=BYTES_ENCODED)
        package_test_function(self, package, b"ABCD", "D", "B", 4, 0)
        self.assertFalse(package.is_handshake())
        self.assertFalse(package.is_error())

    def testIncoherentHeadToPackage(self):
        # head says payload's length is 3, but it's 4
        # b'DB\x04\x00\x00\x00\x00\x00\x00\x00ABCD1997'
        encoded = b'DB\x03\x00\x00\x00\x00\x00\x00\x00ABCD1997'
        package = Package(encoded=encoded)
        package_test_function(self, package, b"", "E", "B", 0, 0)
        self.assertFalse(package.is_handshake())
        self.assertTrue(package.is_error())

    def testParseCorruptedStreamToPackage(self):
        # encoded is a bunch of hex chars
        # b'\xfffff23fafafa'
        package = Package(encoded=CORRUPTED_STREAM)
        package_test_function(self, package, b"", "E", "B", 0, 0)
        self.assertTrue(package.is_error())
        self.assertFalse(package.is_handshake())

    def testParseCorruptedEndOfPackageToPacakage(self):
        # encoded has a corrupted end of package. If there is 1 error, there could be more;
        # b'DB\x04\x00\x00\x00\x00\x00\x00\x00ABCD1997'
        encoded = b'DB\x04\x00\x00\x00\x00\x00\x00\x00ABCD0000'
        package = Package(encoded=encoded)
        package_test_function(self, package, b"", "E", "B", 0, 0)

    def testCreateHandshakePackage(self):
        package = Package(code="H")
        package_test_function(self, package, b"", "H", "B", 0, 0)
        self.assertTrue(package.is_handshake())
        self.assertFalse(package.is_error())


class TestSplitter(unittest.TestCase):
    def testBytesSizeIsMultipleOfPayloadSize(self):
        bytes_for_testing = ("1"*114*3).encode()
        splitter = Splitter(bytes_for_testing)
        result_must_be = [("1"*114).encode()]*3
        self.assertEqual(splitter.splitted, result_must_be)

    def testBytesSizeIsNotMultipleOfPayloadSize(self):
        bytes_for_testing = ("1"*114*3).encode() + ("1"*70).encode()
        splitter = Splitter(bytes_for_testing)
        result_must_be = [("1"*114).encode()]*3 + [("1"*70).encode()]
        self.assertEqual(splitter.splitted, result_must_be)


class TestQueue(unittest.TestCase):
    def testEmptyQueue(self):
        encoded = b''
        splitted = Splitter(encoded).splitted
        queue = PackageQueue(splitted)
        self.assertIsNone(queue.get_next())
        self.assertFalse(queue.has_next())

    def testImageToQueue(self):
        splitted = Splitter(IMAGE).splitted
        queue = PackageQueue(splitted)
        self.assertTrue(queue.has_next())  # first
        while queue.has_next():
            queue.get_next()
        self.assertIsNone(queue.get_next())


def parser_test_function(this: unittest.TestCase, parser: Parser,
                         code: str, dtype: str, length: int, payload, remaining: int):
    this.assertEqual(parser.code, code)
    this.assertEqual(parser.dtype, dtype)
    this.assertEqual(parser.length, length)
    this.assertEqual(parser.payload, payload)
    this.assertEqual(parser.remaining, remaining)


def head_test_function(this: unittest.TestCase, head: Head,
                       code: str, dtype: str, length: int, remaining: int,
                       encoded: bytes = None):
    this.assertTrue(head.is_valid())
    this.assertEqual(head.code, code)
    this.assertEqual(head.dtype, dtype)
    this.assertEqual(head.length, length)
    this.assertEqual(head.remaining, remaining)
    this.assertEqual(head.decoded, (code, dtype, length, remaining))
    if encoded:
        this.assertEqual(head.encoded, encoded)


def payload_test_function(this: unittest.TestCase, payload: Payload, data, dtype: str,
                          length: int, encoded: bytes = None):
    this.assertTrue(payload.is_valid())
    this.assertEqual(payload.data, data)
    this.assertEqual(payload.dtype, dtype)
    this.assertEqual(payload.length, length)
    if encoded:
        this.assertEqual(payload.encoded, encoded)


def eop_test_function(this: unittest.TestCase, package: Package):
    this.assertEqual(package.end_of_package, DEFAULT_EOP)


def package_test_function(this: unittest.TestCase, package: Package, data, code, dtype,
                          length, remaining):
    this.assertTrue(package.is_valid())
    head_test_function(this, package.head, code, dtype, length, remaining)
    payload_test_function(this, package.payload, data, dtype, length)
    eop_test_function(this, package)


if __name__ == "__main__":
    unittest.main(verbosity=2)
