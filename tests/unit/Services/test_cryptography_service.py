import hashlib
import unittest
from unittest.mock import Mock

from services import CryptographyService


class TestCryptographyService(unittest.TestCase):

    def test_find_merkle_root_for_list(self):
        tx1 = Mock()
        tx2 = Mock()
        tx3 = Mock()
        tx4 = Mock()
        tx5 = Mock()
        tx1.to_hash.return_value = self._hash_string("tx1")
        tx2.to_hash.return_value = self._hash_string("tx2")
        tx3.to_hash.return_value = self._hash_string("tx3")
        tx4.to_hash.return_value = self._hash_string("tx4")
        tx5.to_hash.return_value = self._hash_string("tx5")

        transactions = [tx1, tx2, tx3, tx4, tx5]
        transaction_hashes = [tx.to_hash() for tx in transactions]

        service = CryptographyService()
        merkle_root = service.find_merkle_root_for_list(transaction_hashes)

        assert merkle_root == '9093ce34957e2125a1156dca393ab6ed07ed7f4522c8fc2f35c4ccb1378dc3ba'


    def _hash_string(self, data: str) -> str:
        return hashlib.sha256(data.encode('ascii')).hexdigest()

if __name__ == '__main__':
    unittest.main()
