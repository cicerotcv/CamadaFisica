from camfis_utils import EOP, PAYLOAD_SIZE
from typing import Union, List
from package import Package, Default


class Splitter():
    def __init__(self, data: bytes):
        self.splitted = self.split(data)

    def split(self, data) -> list:
        # data = [1, 2, 3, 4, 5, 6, 7, 8, 9]
        # [[1, 2, 3, 4], [5, 6, 7, 8], [9]] nº elementos = (len(data) + 1) // 2

        n_elements = (len(data) + PAYLOAD_SIZE - 1) // PAYLOAD_SIZE
        partitions = [data[i*PAYLOAD_SIZE: (i+1)*PAYLOAD_SIZE]
                      for i in range(n_elements)]
        return partitions


class PackageQueue():
    def __init__(self, partitions: list):
        self.elements = self.get_elements(partitions)
        self.current = 1
        self.length = len(self.elements)

    def get_elements(self, partitions) -> list:
        elements = []
        for index, message in enumerate(partitions):
            current_package = index + 1
            total_packages = len(partitions)
            package = Default(message, 1, 2, current_package, total_packages)
            elements.append(package)
        return elements

    def get_next(self) -> Package:
        if self.has_next():
            next = self.elements[self.current-1]
            self.current += 1
            return next

    def get_nth(self, n: int):
        """1 <= n <= self.length"""
        previous = self.elements[n-1]
        self.current = n+1
        return previous

    def has_next(self):
        # self.length = 2
        # self.current = 1
        # deve retornar True
        return (self.current <= self.length) and (self.length > 0)


class Storage():
    def __init__(self):
        self.partitions = []
        self.size = 0

    def insert(self, pkg: Package):
        if pkg.head.current_package <= self.size+1:
            self.partitions.append(pkg)
        else:
            self.partitions[pkg.head.current_package] = pkg
        self.set_size()

    def remove_last(self):
        if self.size > 0:
            self.set_partitions(self.partitions[:-1])

    def set_partitions(self, new_partitions):
        self.partitions = new_partitions
        self.set_size()

    def set_size(self) -> int:
        size = sum([package.payload.length for package in self.partitions])
        self.size = size


class Assembler():
    def __init__(self, storage: Storage):
        self.storage = storage
        self.assembled = None

    def assemble(self):
        assembled = b"".join([
            package.payload() for package in self.storage.partitions
        ])
        self.assembled = assembled

    def write(self, filename: str):
        if self.assembled == None:
            self.assemble()
        with open(filename, 'wb') as file:
            file.write(self.assembled)
