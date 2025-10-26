import unittest

import pytest

class TestMiningWorkflow(unittest.TestCase):

    @pytest.mark.skip(reason="TODO")
    def test_miner_selects_between_5_and_10_valid_transactions(self):
        """
        Miner must choose minimum 5 and maximum 10 valid transactions from the pool.
        """
        pass

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
