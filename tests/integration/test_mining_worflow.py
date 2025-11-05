import os
import tempfile
import unittest
from decimal import Decimal

import pytest

from blockchain.ledger import Ledger
from exceptions.mining import InvalidBlockException
from models import User, Transaction, Block
from services import FileSystemService


class TestMiningWorkflow(unittest.TestCase):

    def setUp(self):
        tmp_path = tempfile.TemporaryDirectory().name
        ledger_file_path = os.path.join(tmp_path, FileSystemService.DATA_DIR_NAME, FileSystemService.LEDGER_FILE_NAME)
        self.pool_file_path = ledger_file_path

        os.makedirs(os.path.dirname(ledger_file_path), exist_ok=True)

        filesystem_service = FileSystemService()
        filesystem_service.create_file(ledger_file_path)

        Ledger.destroy_instance()
        Ledger.create_instance(file_path=ledger_file_path)

    @pytest.mark.integration
    def test_miner_selects_between_5_and_10_valid_transactions(self):
        """
        Miner must choose minimum 5 and maximum 10 valid transactions from the pool.
        """
        user1 = User.create_for_test("miner1", "password1")
        user2 = User.create_for_test("user2", "password2")

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

    @pytest.mark.skip(reason="TODO")
    def test_mining_strategy_cannot_be_biased(self):
        """
        Miner cannot exclusively choose their own transactions or ignore zero-fee/low-fee ones permanently.
        Strategy must eventually include all valid pool transactions.
        """
        pass

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
