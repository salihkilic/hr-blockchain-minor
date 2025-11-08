import os
import unittest
from decimal import Decimal
from unittest.mock import patch

import pytest
import tempfile

from blockchain import Pool
from blockchain.ledger import Ledger
from exceptions.mining import InvalidBlockException
from models import Block, User, Transaction
from models.constants import FilesAndDirectories
from services import FileSystemService, InitializationService


class TestMining(unittest.TestCase):

    @patch("services.filesystem_service.FileSystemService.get_data_root", side_effect=FileSystemService.get_temp_data_root)
    def setUp(self, mock_get_data_root):
        FileSystemService.clear_temp_data_root()
        InitializationService.initialize_application()

    @pytest.mark.integration
    @patch("repositories.user.UserRepository.username_exists", return_value=False)
    @patch("services.filesystem_service.FileSystemService.get_data_root", side_effect=FileSystemService.get_temp_data_root)
    @patch("models.transaction.Transaction.validate", return_value=True)
    def test_block_mining_requires_minimum_five_valid_transactions(self, mock_username_exists, mock_get_data_root, mock_transaction_validate):
        """
        A new block could be mined, if there are a minimum of 5 valid transactions on the pool.
        """
        sender = User.create("dummy_sender", "dummy_sender_pass")
        receiver = User.create("dummy_receiver", "dummy_receiver_pass")
        miner = User.create("dummy_miner", "dummy_miner_pass")

        # Too few transactions
        with pytest.raises(InvalidBlockException):
            transactions = [Transaction.create(sender, receiver.address, Decimal(10.0), fee=Decimal(0.1)) for _ in range(4)]
            Block.mine_with_transactions(miner, transactions)

        # Sufficient transactions
        transactions = [Transaction.create(sender, receiver.address, Decimal(10.0), fee=Decimal(0.1)) for _ in range(5)]
        mined_block = Block.mine_with_transactions(miner, transactions)
        assert mined_block is not None



    @pytest.mark.skip(reason="TODO")
    def test_block_mining_requires_previous_blocks_have_three_valid_flags(self):
        """
        A new block could be mined after the last block, only if every previous block in the chain has at least 3 valid flags.
        """
        pass

    @pytest.mark.skip(reason="TODO")
    def test_block_mining_time_between_10_and_20_seconds(self):
        """
        A block must be mined between 10 to 20 seconds (via Proof of Work).
        NOTE: No artificial delays like sleep allowed — must be enforced by difficulty.
        """
        pass

    @pytest.mark.skip(reason="TODO")
    def test_block_mining_interval_is_at_least_3_minutes(self):
        """
        A minimum of 3 minutes interval must be between every two consequent blocks.
        """
        pass

    @pytest.mark.skip(reason="TODO")
    def test_miner_receives_50_coin_reward(self):
        """
        A miner will receive 50 coins, as a mining reward for a successful block addition to the chain.
        """
        pass

if __name__ == '__main__':
    unittest.main()
