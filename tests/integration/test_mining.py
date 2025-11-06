import os
import unittest
from decimal import Decimal

import pytest
import tempfile

from blockchain import Pool
from blockchain.ledger import Ledger
from exceptions.mining import InvalidBlockException
from models import Block, User, Transaction
from models.constants import FilesAndDirectories
from services import FileSystemService


class TestMining(unittest.TestCase):

    def setUp(self):
        tmp_path = tempfile.TemporaryDirectory().name
        ledger_file_path = os.path.join(tmp_path, FilesAndDirectories.DATA_DIR_NAME, FilesAndDirectories.LEDGER_FILE_NAME)
        self.pool_file_path = ledger_file_path

        os.makedirs(os.path.dirname(ledger_file_path), exist_ok=True)

        filesystem_service = FileSystemService(repo_root=tmp_path)
        filesystem_service.initialize_data_files()

        Ledger.destroy_instance()
        Ledger.get_instance(file_path=ledger_file_path)

        Pool.destroy_instance()
        Pool.get_instance(file_path=self.pool_file_path)


    def test_block_mining_requires_minimum_five_valid_transactions(self):
        """
        A new block could be mined, if there are a minimum of 5 valid transactions on the pool.
        """
        sender = User.create_for_test("dummy_sender", "dummy_sender_pass")
        receiver = User.create_for_test("dummy_receiver", "dummy_receiver_pass")
        miner = User.create_for_test("dummy_miner", "dummy_miner_pass")

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
