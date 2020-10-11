from camfis_utils import EOP, PAYLOAD_SIZE 
from typing import Union, List
from package import Package


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
        for index, element in enumerate(partitions):
            remaining = len(partitions) - (index + 1)
            package = Package(content=element, code="D", remaining=remaining)
            elements.append(package)
        return elements

    def get_next(self):
        if self.has_next():
            next = self.elements[self.current]
            self.current += 1
            return next

    def get_previous(self):
        previous = self.elements[self.current - 1]
        return previous

    def has_next(self):
        # self.length = 2
        # self.current = 1
        # deve retornar True
        return (self.current <= self.length - 1) and (self.length > 0)


class Storage():
    def __init__(self):
        self.partitions = []
        self.size = 0

    def insert(self, pkg: Package):
        self.partitions.append(pkg)

    def remove_last(self):
        if self.size > 0:
            self.set_partitions(self.partitions[:-1])

    def set_partitions(self, new_partitions):
        self.partitions = new_partitions
        self.size = self.get_size()

    def get_size(self) -> int:
        size = sum([package.payload.length for package in self.partitions])
        return size


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
