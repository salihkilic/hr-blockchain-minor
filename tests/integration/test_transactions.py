import unittest

import pytest


class TestTransactions(unittest.TestCase):
    @pytest.mark.skip(reason="TODO")
    def test_transaction_can_have_fee_value(self):
        """
        An extra value could be placed on a transaction as transaction fee.
        """
        pass

    @pytest.mark.skip(reason="TODO")
    def test_sender_must_enter_transaction_fee(self):
        """
        A sender must enter the transaction fee while creating a transaction.
        """
        pass

    @pytest.mark.skip(reason="TODO")
    def test_transaction_fee_provides_incentive_for_miners(self):
        """
        The transaction fee is incentive to motivate miners to pick a transaction for their new block.
        """
        pass


if __name__ == '__main__':
    unittest.main()
