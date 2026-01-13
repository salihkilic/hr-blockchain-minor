import unittest
import os
from decimal import Decimal
from unittest.mock import patch, MagicMock

import pytest

from blockchain.ledger import Ledger
from blockchain import Pool
from exceptions.mining import InvalidBlockException
from models import Block, User, Transaction
from services import FileSystemService, InitializationService, NetworkingService, NodeFileSystemService


class TestMining(unittest.TestCase):

    def setUp(self):
        # Patch FileSystemService
        self.fs_patcher = patch("services.filesystem_service.FileSystemService.get_data_root", side_effect=FileSystemService.get_temp_data_root)
        self.mock_get_data_root = self.fs_patcher.start()
        self.addCleanup(self.fs_patcher.stop)

        # Patch NodeFileSystemService.get_data_root
        def get_node_temp_root(self_instance=None, create_if_missing=False):
            root = os.path.join(FileSystemService.get_temp_data_root(), "node_data")
            if create_if_missing and not os.path.exists(root):
                os.makedirs(root)
            return root

        self.nfs_patcher = patch("services.node_filesystem_service.NodeFileSystemService.get_data_root", side_effect=get_node_temp_root)
        self.mock_node_get_data_root = self.nfs_patcher.start()
        self.addCleanup(self.nfs_patcher.stop)

        # Patch NetworkingService.get_instance
        self.ns_patcher = patch("services.networking_service.NetworkingService.get_instance")
        self.mock_get_instance = self.ns_patcher.start()
        self.mock_ns = MagicMock()
        self.mock_get_instance.return_value = self.mock_ns
        self.addCleanup(self.ns_patcher.stop)

        # Clean state
        FileSystemService.clear_temp_data_root()

        Ledger.destroy_instance()
        Pool.destroy_instance()
        # NetworkingService.destroy_instance() # Not needed as we mock get_instance
        NodeFileSystemService._node_data_directory = None

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

        # Make find_by_address return real users
        address_book = {
            user_miner.address: user_miner,
            validator1.address: validator1,
            validator2.address: validator2,
            validator3.address: validator3,
            receiver.address: receiver,
        }
        mock_find_by_address.side_effect = lambda addr: address_book.get(addr)

        # Create 5 transactions and add them to pool for fairness validation
        txs = [Transaction.create(user_miner, receiver.address, Decimal(1 + i), fee=Decimal(0)) for i in range(5)]
        for tx in txs:
            Pool.get_instance().add_transaction(tx)

        ledger = Ledger.get_instance()
        # Make genesis timestamp sufficiently earlier to satisfy 3-minute spacing rule
        from datetime import datetime, timedelta
        genesis = ledger.get_latest_block()
        if genesis is not None:
            gen_ts = datetime.fromisoformat(genesis.timestamp)
            genesis.timestamp = (gen_ts - timedelta(seconds=181)).isoformat()

        # Keep mining difficulty fixed and prevent ramp-up during this test
        from services.difficulty_service import DifficultyService, MAX_TARGET
        with patch.object(DifficultyService, "current_difficulty", MAX_TARGET), \
             patch.object(DifficultyService, "update_time_to_mine", autospec=True) as upd_mock:
            upd_mock.return_value = None

            # Mine first block (returns block object)
            pending_block = Block.mine_with_transactions(user_miner, txs)
            # Submit it to ledger as pending (consensus starts)
            ledger.submit_block(pending_block)
            assert pending_block.status is not None and pending_block.status.value == 'pending'

            # Attempt to submit next block should fail (previous block still pending)
            txs2 = [Transaction.create(user_miner, receiver.address, Decimal(10 + i), fee=Decimal(0)) for i in range(5)]
            second_block = Block.mine_with_transactions(user_miner, txs2)
            with pytest.raises(InvalidBlockException):
                ledger.submit_block(second_block)

            # Add two valid flags - still should not allow new block submission
            ledger.add_validation_flag(pending_block.calculated_hash, validator1.address, valid=True)
            ledger.add_validation_flag(pending_block.calculated_hash, validator2.address, valid=True)
            second_block = Block.mine_with_transactions(user_miner, txs2)
            with pytest.raises(InvalidBlockException):
                ledger.submit_block(second_block)

            # Third valid flag finalizes block
            ledger.add_validation_flag(pending_block.calculated_hash, validator3.address, valid=True)
            assert ledger.get_latest_block().calculated_hash == pending_block.calculated_hash
            assert pending_block.status.value == 'accepted'

            # Now mining next block should succeed (submission may still be constrained by 3-minute spacing rule)
            second_block = Block.mine_with_transactions(user_miner, txs2)
            assert second_block is not None

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
