import os
import tempfile
import unittest
from decimal import Decimal, ROUND_DOWN
from unittest.mock import patch

from _pytest.tmpdir import tmp_path

from blockchain import Pool
from models import User, Transaction
from models.constants import FilesAndDirectories
from services import FileSystemService, InitializationService


class TestPool(unittest.TestCase):

    _user_addresses = {}

    @patch("services.filesystem_service.FileSystemService.get_data_root",
           side_effect=FileSystemService.get_temp_data_root)
    def setUp(self, mock_get_data_root):
        FileSystemService.clear_temp_data_root()
        InitializationService.initialize_application()
        Pool.destroy_instance()
        self.__class__._user_addresses = {}

    @patch("services.filesystem_service.FileSystemService.get_data_root",
           side_effect=FileSystemService.get_temp_data_root)
    @patch("repositories.user.UserRepository.find_by_address",
           side_effect=lambda address: TestPool._user_addresses.get(address))
    @patch("models.wallet.Wallet.balance", new_callable=lambda: Decimal("10000.0"))
    def test_pool_saving_to_disk(self, mock_balance, mock_find_by_address, mock_get_data_root):
        user1 = User.create("sender", "password")
        user2 = User.create("receiver", "password")

        self.__class__._user_addresses[user1.address] = user1
        self.__class__._user_addresses[user2.address] = user2

        transaction = Transaction.create(user1, user2.address, Decimal(10.0), Decimal(0.1))

        Pool.get_instance().add_transaction(transaction)

        # Reload the pool from disk
        Pool.destroy_instance()
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
