from constants import DEFAULT_EOP, PAYLOAD_SIZE, get_code, get_length
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
        self.queue = self.get_queue(partitions)
        self.current = 0
        self.length = len(self.queue)

    def get_queue(self, partitions) -> list:
        queue = []
        for index, element in enumerate(partitions):
            remaining = len(partitions) - (index + 1)
            package = Package(content=element, code="D", remaining=remaining)
            queue.append(package)
        return queue

    def get_next(self):
        if self.has_next():
            next = self.queue[self.current]
            self.current += 1
            return next

    def has_next(self):
        return self.current < len(self.queue)
