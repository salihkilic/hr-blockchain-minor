import unittest
from datetime import datetime, timezone
from decimal import Decimal
from unittest.mock import patch

import pytest

from blockchain import Pool
from exceptions.mining import InvalidBlockException
from models import User, Transaction, Block
from services import FileSystemService, InitializationService


class TestMiningWorkflow(unittest.TestCase):

    @patch("services.filesystem_service.FileSystemService.get_data_root",
           side_effect=FileSystemService.get_temp_data_root)
    def setUp(self, mock_get_data_root):
        FileSystemService.clear_temp_data_root()
        InitializationService.initialize_application()

    @pytest.mark.integration
    @patch("services.filesystem_service.FileSystemService.get_data_root",
           side_effect=FileSystemService.get_temp_data_root)
    @patch("models.transaction.Transaction.validate", return_value=True)
    def test_miner_selects_between_5_and_10_valid_transactions(self, mock_get_data_root, mock_transaction_validate):
        """
        Miner must choose minimum 5 and maximum 10 valid transactions from the pool.
        """
        user1 = User.create("miner1", "password1")
        user2 = User.create("user2", "password2")

        transaction1 = Transaction.create(user1, user2.address, Decimal(10.0), fee=Decimal(0.1))
        transaction2 = Transaction.create(user2, user1.address, Decimal(5.0), fee=Decimal(0.05))
        transaction3 = Transaction.create(user1, user2.address, Decimal(20.0), fee=Decimal(0.2))
        transaction4 = Transaction.create(user2, user1.address, Decimal(15.0), fee=Decimal(0.15))
        transaction5 = Transaction.create(user1, user2.address, Decimal(30.0), fee=Decimal(0.3))
        transaction6 = Transaction.create(user2, user1.address, Decimal(25.0), fee=Decimal(0.25))
        transaction7 = Transaction.create(user1, user2.address, Decimal(12.0), fee=Decimal(0.12))
        transaction8 = Transaction.create(user2, user1.address, Decimal(18.0), fee=Decimal(0.18))
        transaction9 = Transaction.create(user1, user2.address, Decimal(22.0), fee=Decimal(0.22))
        transaction10 = Transaction.create(user2, user1.address, Decimal(28.0), fee=Decimal(0.28))
        transaction11 = Transaction.create(user1, user2.address, Decimal(35.0), fee=Decimal(0.35))

        correct_transactions = [
            transaction1,
            transaction2,
            transaction3,
            transaction4,
            transaction5,
            transaction6
        ]
        # Keep difficulty low to mine quickly in tests
        from services.difficulty_service import DifficultyService, MAX_TARGET
        with patch.object(DifficultyService, "current_difficulty", MAX_TARGET), \
             patch.object(DifficultyService, "update_time_to_mine", autospec=True) as upd_mock:
            upd_mock.return_value = None
            block = Block.mine_with_transactions(
                miner=user1,
                transactions=correct_transactions
            )

        too_few_transactions = [
            transaction1,
            transaction2,
            transaction3
        ]

        with pytest.raises(InvalidBlockException) as excinfo:
            block = Block.mine_with_transactions(
                miner=user1,
                transactions=too_few_transactions
            )

        assert excinfo.value.__str__() == "Block must contain between 5 and 10 valid transactions."

        too_many_transactions = [
            transaction1,
            transaction2,
            transaction3,
            transaction4,
            transaction5,
            transaction6,
            transaction7,
            transaction8,
            transaction9,
            transaction10,
            transaction11
        ]

        with pytest.raises(InvalidBlockException) as excinfo:
            block = Block.mine_with_transactions(
                miner=user1,
                transactions=too_many_transactions
            )

        assert excinfo.value.__str__() == "Block must contain between 5 and 10 valid transactions."

    @pytest.mark.integration
    @patch("services.filesystem_service.FileSystemService.get_data_root",
           side_effect=FileSystemService.get_temp_data_root)
    @patch("models.transaction.Transaction.validate", return_value=True)
    def test_mining_strategy_cannot_be_biased(self, mock_get_data_root, mock_transaction_validate):
        """
        Miner cannot exclusively choose their own transactions or ignore zero-fee/low-fee ones permanently.
        Strategy must eventually include all valid pool transactions.
        """

        user1 = User.create("miner1", "password1")
        user2 = User.create("user2", "password2")

        transactions = [
            Transaction.create(user1, user2.address, Decimal(10.0), fee=Decimal(0.1)),
            Transaction.create(user2, user1.address, Decimal(5.0), fee=Decimal(0.05)),
            Transaction.create(user1, user2.address, Decimal(20.0), fee=Decimal(0.2)),
            Transaction.create(user2, user1.address, Decimal(15.0), fee=Decimal(0.15)),
            Transaction.create(user1, user2.address, Decimal(30.0), fee=Decimal(0.3)),
            Transaction.create(user2, user1.address, Decimal(25.0), fee=Decimal(0.25)),
            Transaction.create(user1, user2.address, Decimal(12.0), fee=Decimal(0.0012)),
            Transaction.create(user2, user1.address, Decimal(18.0), fee=Decimal(0.18)),
            Transaction.create(user1, user2.address, Decimal(22.0), fee=Decimal(0.22)),
            Transaction.create(user2, user1.address, Decimal(28.0), fee=Decimal(0.28)),
            Transaction.create(user1, user2.address, Decimal(35.0), fee=Decimal(0.0035))
        ]

        for tx in transactions:
            Pool.get_instance().add_transaction(tx)

        required_transactions = Pool.get_instance().get_required_transactions()

        assert required_transactions is not None
        assert len(required_transactions) == 4
        assert required_transactions[0] == transactions[0]  # Oldest transaction
        assert required_transactions[1] == transactions[1]  # Second oldest transaction
        assert required_transactions[2] == transactions[6]  # Lowest fee transaction
        assert required_transactions[3] == transactions[10] # Second lowest fee transaction

        fake_mine_timestamp = datetime.now(timezone.utc).isoformat()

        extra_transactions = [
            Transaction.create(user1, user2.address, Decimal(40.0), fee=Decimal(0)),
            Transaction.create(user2, user1.address, Decimal(45.0), fee=Decimal(0.045))
        ]

        for tx in extra_transactions:
            Pool.get_instance().add_transaction(tx)

        required_transactions_after_block_mined = Pool.get_instance().get_required_transactions(max_timestamp=fake_mine_timestamp)

        assert required_transactions_after_block_mined is not None
        assert len(required_transactions_after_block_mined) == 4
        assert required_transactions_after_block_mined[0] == transactions[0]  # Oldest transaction
        assert required_transactions_after_block_mined[1] == transactions[1]  # Second oldest transaction
        assert required_transactions_after_block_mined[2] == transactions[6]  # Lowest fee transaction
        assert required_transactions_after_block_mined[3] == transactions[10] # Second lowest fee transaction

        # Keep difficulty low and stable during block mining for fairness checks
        from services.difficulty_service import DifficultyService, MAX_TARGET
        with patch.object(DifficultyService, "current_difficulty", MAX_TARGET), \
             patch.object(DifficultyService, "update_time_to_mine", autospec=True) as upd_mock:
            upd_mock.return_value = None

            fair_block = Block.mine_with_transactions(
                miner=user1,
                transactions=[
                    transactions[0],
                    transactions[1],
                    transactions[6],
                    transactions[10],
                    extra_transactions[0]
                ]
            )

            Pool.get_instance().validate_transaction_in_block_for_fairness(fair_block)

            unfair_block = Block.mine_with_transactions(
                miner=user1,
                transactions=[
                    transactions[0],
                    transactions[2],
                    transactions[4],
                    transactions[6],
                    transactions[8]
                ]
            )

        # Only own transactions
        with pytest.raises(InvalidBlockException) as excinf:
            Pool.get_instance().validate_transaction_in_block_for_fairness(unfair_block)

        assert excinf.value.__str__() == "Not all required transactions are included in the block for fairness."


    @pytest.mark.skip(reason="TODO")
    def test_miner_prioritizes_high_transaction_fees_but_includes_others_eventually(self):
        """
        Miner may select high-fee transactions first, but must not permanently exclude lower-fee ones.
        """
        pass

    @pytest.mark.skip(reason="TODO")
    def test_invalid_transactions_are_flagged_by_miner(self):
        """
        While mining, invalid transactions in pool must be flagged as invalid.
        """
        pass

    @pytest.mark.skip(reason="TODO")
    def test_miner_cannot_validate_own_block(self):
        """
        Miner (block creator) cannot be one of the validating nodes for the mined block.
        """
        pass

    @pytest.mark.skip(reason="TODO")
    def test_three_nodes_validate_a_good_block(self):
        """
        If three different validator nodes mark the block valid, it becomes validated
        and does not require more validators.
        """
        pass

    @pytest.mark.skip(reason="TODO")
    def test_third_validator_creates_reward_transaction_for_miner(self):
        """
        The third node that validates the block must create a reward transaction for the miner.
        Reward transaction goes to the pool.
        """
        pass

    @pytest.mark.skip(reason="TODO")
    def test_block_rejected_after_three_invalid_flags(self):
        """
        If at least three different nodes reject the block (before it is validated by three users),
        the block is marked invalid.
        """
        pass

    @pytest.mark.skip(reason="TODO")
    def test_rejected_block_returns_valid_transactions_to_pool(self):
        """
        Valid transactions from a rejected block must go back to the pool.
        Pending previous for next mining.
        """
        pass

    @pytest.mark.skip(reason="TODO")
    def test_rejected_block_invalid_transactions_remain_flagged(self):
        """
        Invalid transactions from rejected block must remain flagged as invalid in the pool.
        These must later be auto-canceled when their creator logs in.
        """
        pass


if __name__ == '__main__':
    unittest.main()
