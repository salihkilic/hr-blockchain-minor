import os
import tempfile
import unittest
from decimal import Decimal
from unittest.mock import patch

import pytest

from blockchain.ledger import Ledger
from models import User, Transaction, Block
from models.constants import FilesAndDirectories
from services import FileSystemService, InitializationService


class TestLedger(unittest.TestCase):

    _user_addresses = {}

    @patch("services.filesystem_service.FileSystemService.get_data_root",
           side_effect=FileSystemService.get_temp_data_root)
    def setUp(self, mock_get_data_root):
        FileSystemService.clear_temp_data_root()
        InitializationService.initialize_application()
        Ledger.destroy_instance()
        self.__class__._user_addresses = {}

    @pytest.mark.unit
    @patch("services.filesystem_service.FileSystemService.get_data_root",
           side_effect=FileSystemService.get_temp_data_root)
    @patch("repositories.user.UserRepository.find_by_address",
           side_effect=lambda address: TestLedger._user_addresses.get(address))
    @patch("models.wallet.Wallet.balance", new_callable=lambda: Decimal("10000.0"))
    def test_with_transactions(self, mock_balance, mock_find_by_address, mock_get_data_root):
        user1 = User.create("user1", "password1") # Wallet 50
        user2 = User.create("user2", "password2") # Wallet 50
        user3 = User.create("user3", "password3") # Wallet 50

        self.__class__._user_addresses[user1.address] = user1
        self.__class__._user_addresses[user2.address] = user2
        self.__class__._user_addresses[user3.address] = user3

        transactions = [
            Transaction.create(user1, user2.address, Decimal(10), Decimal(0.1)),  # user1 (50, 39.9) -> user2 (60.1)
            Transaction.create(user2, user3.address, Decimal(20), Decimal(0.2)),  # user2 (60.1, 39.9) -> user3 (70)
            Transaction.create(user3, user1.address, Decimal(5), Decimal(0.05)),   # user3 (70, 64.95) -> user1 (44.95)
            Transaction.create(user1, user3.address, Decimal(15), Decimal(0.15)), # user1 (44.95, 29.8) -> user3 (79.95)
            Transaction.create(user2, user1.address, Decimal(10), Decimal(0.1)),  # user2 (39.9, 29.8) -> user1 (39.8)
        ]

        block = Block.mine_with_transactions(
            miner=user1,
            transactions=transactions
        )

        Ledger.get_instance().add_block(block)

        latest_block = Ledger.get_instance().get_latest_block()
        self.assertIsNotNone(latest_block)
        self.assertEqual(latest_block.calculated_hash, block.calculated_hash)
        self.assertEqual(len(latest_block.transactions), len(transactions))

        # Destroy and reload the ledger to verify persistence
        Ledger.destroy_instance()
        reloaded_latest_block = Ledger.get_instance().get_latest_block()
        self.assertIsNotNone(reloaded_latest_block)
        self.assertEqual(reloaded_latest_block.calculated_hash, block.calculated_hash)
        self.assertEqual(len(reloaded_latest_block.transactions), len(transactions))

    @pytest.mark.unit
    @patch("services.filesystem_service.FileSystemService.get_data_root",
           side_effect=FileSystemService.get_temp_data_root)
    def test_find_block_by_nr_for_genesis_block(self, mock_get_data_root):
        ledger = Ledger.get_instance()

        genesis_block = ledger.get_block_by_number(0)
        self.assertIsNotNone(genesis_block)
        self.assertEqual(genesis_block.number, 0)


    @pytest.mark.skip(reason="TODO")
    def test_validates_that_transactions_are_in_the_pool(self):
        pass


