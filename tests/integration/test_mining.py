import unittest
from decimal import Decimal
from unittest.mock import patch

import pytest

from blockchain.ledger import Ledger
from exceptions.mining import InvalidBlockException
from models import Block, User, Transaction
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


    @patch("services.filesystem_service.FileSystemService.get_data_root", side_effect=FileSystemService.get_temp_data_root)
    @patch("models.transaction.Transaction.validate", return_value=True)
    @patch("repositories.user.UserRepository.username_exists", return_value=False)
    @patch("repositories.user.UserRepository.find_by_address", side_effect=lambda address: None)
    def test_block_mining_requires_previous_blocks_have_three_valid_flags(self, mock_find_by_address, mock_username_exists, mock_tx_validate, mock_get_data_root):
        """
        A new block could be mined after the last block, only if every previous block in the chain has at least 3 valid flags.
        Implemented by disallowing submission of a new block while a block is pending (before 3 valid flags finalize it).
        """
        # Setup users
        user_miner = User.create("minerA", "passA")
        validator1 = User.create("val1", "pass1")
        validator2 = User.create("val2", "pass2")
        validator3 = User.create("val3", "pass3")
        receiver = User.create("recv", "passR")

        # Create 5 transactions
        txs = [Transaction.create(user_miner, receiver.address, Decimal(1 + i), fee=Decimal(0)) for i in range(5)]

        ledger = Ledger.get_instance()

        # Mine first block (returns block object)
        pending_block = Block.mine_with_transactions(user_miner, txs)
        # Submit it to ledger as pending (consensus starts)
        ledger.submit_block(pending_block)
        assert pending_block.status is not None and pending_block.status.value == 'pending'

        # Attempt to mine next block should fail (pending not validated yet)
        txs2 = [Transaction.create(user_miner, receiver.address, Decimal(10 + i), fee=Decimal(0)) for i in range(5)]
        with pytest.raises(InvalidBlockException):
            second_block = Block.mine_with_transactions(user_miner, txs2)
            ledger.submit_block(second_block)

        # Add two valid flags - still should not allow new block
        ledger.add_validation_flag(pending_block.calculated_hash, validator1.address, valid=True)
        ledger.add_validation_flag(pending_block.calculated_hash, validator2.address, valid=True)
        with pytest.raises(InvalidBlockException):
            second_block = Block.mine_with_transactions(user_miner, txs2)
            ledger.submit_block(second_block)

        # Third valid flag finalizes block
        ledger.add_validation_flag(pending_block.calculated_hash, validator3.address, valid=True)
        assert ledger.get_latest_block().calculated_hash == pending_block.calculated_hash
        assert pending_block.status.value == 'accepted'

        # Now mining next block should succeed
        second_block = Block.mine_with_transactions(user_miner, txs2)
        ledger.submit_block(second_block)
        assert second_block.status.value == 'pending'

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
