import os
import tempfile
import unittest
from decimal import Decimal, ROUND_DOWN

from _pytest.tmpdir import tmp_path

from blockchain import Pool
from models import User, Transaction
from services import FileSystemService


class MyTestCase(unittest.TestCase):

    def setUp(self):
        tmp_path = tempfile.TemporaryDirectory().name
        pool_file_path = os.path.join(tmp_path, FileSystemService.DATA_DIR_NAME, FileSystemService.POOL_FILE_NAME)
        self.pool_file_path = pool_file_path

        os.makedirs(os.path.dirname(pool_file_path), exist_ok=True)

        filesystem_service = FileSystemService()
        filesystem_service.create_file(pool_file_path)

        Pool.destroy_instance()
        Pool.create_instance(file_path=pool_file_path)

    def test_pool_saving_to_disk(self):
        user1 = User.create_for_test("sender", "password")
        user2 = User.create_for_test("receiver", "password")
        transaction = Transaction.create(user1, user2.address, Decimal(10.0), Decimal(0.1))

        Pool.get_instance().add_transaction(transaction)

        # Reload the pool from disk
        Pool.destroy_instance()
        Pool.create_instance(file_path=self.pool_file_path)
        reloaded_pool = Pool.get_instance()
        transactions = reloaded_pool.get_transactions()

        self.assertEqual(len(transactions), 1)
        self.assertEqual(transactions[0].hash, transaction.hash)
        self.assertEqual(transactions[0].sender_address, transaction.sender_address)
        self.assertEqual(transactions[0].sender_signature, transaction.sender_signature)
        self.assertEqual(transactions[0].sender_public_key, transaction.sender_public_key)
        self.assertEqual(transactions[0].receiver_address, transaction.receiver_address)
        self.assertEqual(transactions[0].amount, transaction.amount)
        self.assertEqual(transactions[0].fee, transaction.fee)


if __name__ == '__main__':
    unittest.main()
