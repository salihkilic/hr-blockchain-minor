import os
import tempfile
import unittest
from decimal import Decimal

import pytest

from blockchain.ledger import Ledger
from models import User, Transaction, Block
from services import FileSystemService


class TestLedger(unittest.TestCase):

    def setUp(self):
        tmp_path = tempfile.TemporaryDirectory().name
        ledger_file_path = os.path.join(tmp_path, FileSystemService.DATA_DIR_NAME, FileSystemService.LEDGER_FILE_NAME)
        self.pool_file_path = ledger_file_path

        os.makedirs(os.path.dirname(ledger_file_path), exist_ok=True)

        filesystem_service = FileSystemService()
        filesystem_service.create_file(ledger_file_path)

        Ledger.destroy_instance()
        Ledger.create_instance(file_path=ledger_file_path)

    @pytest.mark.unit
    def test_with_transactions(self):
        user1 = User.create_for_test("user1", "password1") # Wallet 50
        user2 = User.create_for_test("user2", "password2") # Wallet 50
        user3 = User.create_for_test("user3", "password3") # Wallet 50

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
        Ledger.create_instance(file_path=self.pool_file_path)
        reloaded_latest_block = Ledger.get_instance().get_latest_block()
        self.assertIsNotNone(reloaded_latest_block)
        self.assertEqual(reloaded_latest_block.calculated_hash, block.calculated_hash)
        self.assertEqual(len(reloaded_latest_block.transactions), len(transactions))

    @pytest.mark.skip(reason="TODO")
    def test_validates_that_transactions_are_in_the_pool(self):
        pass


