# -*- coding: utf-8 -*-
import unittest
from camfis_utils import EOP

# deve ser da forma \xff\x00\xff\x00


class EndOfPackage():
    def __init__(self, eop:bytes=None):
        """Para criar um end of package, nenhum argumento deve ser inserido;
        Para traduzir, deve-se inserir em "eop" os 4 últimos bytes do pacote.

        Args:
            eop (bytes, optional): [description]. Defaults to None.
        """
        self.eop = self.get_eop(eop) # b'\x00\x00\x00\x00'
    
    def __call__(self):
        return self.eop

    def get_eop(self, eop) -> bytes:
        if eop is not None:
            if eop == EOP:
                return eop
            else:
                return b'\x00\x00\x00\x00'
        else:
            return EOP

    def is_valid(self) -> bool:
        """Devolve True se o End of Package estiver de acordo com o esperado

        Returns:
            bool: End of Package de acord com o esperado
        """
        return self.eop == EOP


class TestEndOfPackage(unittest.TestCase):

    def testCreateEOP(self):
        eop = EndOfPackage()
        self.assertTrue(eop.is_valid())
    
    def testTranslateCorrectEOP(self):
        eop = EndOfPackage(eop=EOP)
        self.assertTrue(eop.is_valid())
