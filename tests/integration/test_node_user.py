import unittest
import pytest

from models import Wallet
from services.user_service import UserService


class TestNodeUser(unittest.TestCase):

    @pytest.mark.skip(reason="TODO")
    def test_user_has_wallet_after_registration(self):
        """ A node user has a wallet. """

        new_user = UserService.register(username="testuser", password="testpassword")
        user_wallet = new_user.wallet

        assert user_wallet is not None
        assert isinstance(user_wallet, Wallet)

    @pytest.mark.skip(reason="TODO")
    def test_user_can_send_coins_to_other_users(self):
        """ A node user can send some coins from their wallet to registered users in the system. """
        pass

    @pytest.mark.skip(reason="TODO")
    def test_user_can_receive_coins_from_other_users(self):
        """ A node user can receive some coins in their wallet from other registered users in the system. """
        pass

    @pytest.mark.skip(reason="TODO")
    def test_user_can_try_mining_new_block(self):
        """ A node user can try mining a new block. """
        pass

    @pytest.mark.skip(reason="TODO")
    def test_user_can_view_wallet_balance(self):
        """ A node user can see their balance on the user page. """
        pass

    @pytest.mark.skip(reason="TODO")
    def test_user_can_view_own_transaction_history(self):
        """ A node user can see the history of their own transactions through a menu. """
        pass

    @pytest.mark.skip(reason="TODO")
    def test_user_can_view_current_transactions_in_pool(self):
        """ A node user can view the current ongoing transactions in the pool. """
        pass

if __name__ == '__main__':
    unittest.main()
