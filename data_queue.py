# -*- coding: utf-8 -*-
from package import Package


class Queue():
    """Fila de packages a serem enviados"""
    def __init__(self, package_list: list = []):
        self.package_list = package_list
        self.length = len(package_list)
        self.current = -1
        self.package = None

        def repeat(self) -> Package:
            """Retorna o último package enviado"""
            return self.package

        def get_package(self) -> Package:
            """Retonar o package a ser enviado"""
            self.current += 1
            index = min([self.current, self.length])
            self.package = self.package_list[index]
            return self.package
