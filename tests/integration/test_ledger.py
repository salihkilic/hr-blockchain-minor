import unittest

import pytest


class TestLedger(unittest.TestCase):

    @pytest.mark.skip(reason="TODO")
    def test_block_has_unique_sequential_id(self):
        """
        Each block has a unique ID (a sequential number starting from Zero for the genesis block).
        """
        pass

    @pytest.mark.skip(reason="TODO")
    def test_block_transaction_count_minimum_five(self):
        """
        Every block must contain a minimum of 5 transactions, including reward transactions.
        """
        pass

    @pytest.mark.skip(reason="TODO")
    def test_block_transaction_count_maximum_ten(self):
        """
        Every block must contain a maximum of 10 transactions, including reward transactions.
        """
        pass


if __name__ == '__main__':
    unittest.main()
