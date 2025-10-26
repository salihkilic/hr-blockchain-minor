import unittest

import pytest


class TestNodeLogin(unittest.TestCase)\
        :
    @pytest.mark.skip("TODO")
    def test_node_automatically_validates_pending_blocks_on_login(self):
        """
        When the user logs in (node becomes active):
        ✅ Node must check if there are any new blocks requiring validation.
        ✅ If so, node automatically starts validating the pending block(s).
        """
        pass

    @pytest.mark.skip("TODO")
    def test_node_automatically_cancels_its_flagged_invalid_transactions(self):
        """
        On login:
        ✅ If the user has flagged/invalid transactions in the pool,
        they must automatically be canceled and removed from pending state.
        """
        pass

    @pytest.mark.skip("TODO")
    def test_node_automatic_actions_only_affect_relevant_items(self):
        """
        On login:
        ✅ Automatic actions must only apply to data related to this node.
        ✅ Should not modify unrelated blocks or other users' transactions.
        """
        pass

    @pytest.mark.skip("TODO")
    def test_no_action_when_nothing_pending_for_node(self):
        """
        On login:
        ✅ If there are no pending blocks to validate or invalid user transactions, 
        the system should not perform unnecessary actions.
        """
        pass


if __name__ == '__main__':
    unittest.main()
