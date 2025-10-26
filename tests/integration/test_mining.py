import unittest

import pytest


class TestMining(unittest.TestCase):

    @pytest.mark.skip(reason="TODO")
    def test_block_mining_requires_minimum_five_valid_transactions(self):
        """
        A new block could be mined, if there are a minimum of 5 valid transactions on the pool.
        """
        pass

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
