import unittest

import pytest

class TestLoginNotifications(unittest.TestCase):

    @pytest.mark.skip(reason="TODO")
    def test_show_blockchain_general_info_on_login(self):
        """
        On login:
        ✅ Show blockchain size, number of transactions, and other general info.
        """
        pass

    @pytest.mark.skip(reason="TODO")
    def test_show_pending_mined_block_status_to_miner(self):
        """
        On login:
        ✅ If user has mined a block that is still pending validation by other nodes,
        notify the miner about its pending status.
        """
        pass

    @pytest.mark.skip(reason="TODO")
    def test_confirmed_or_rejected_block_updates_user_miner_status(self):
        """
        On login:
        ✅ If a user's mined block has been validated or rejected since last login,
        show notification of the result.
        """
        pass

    @pytest.mark.skip(reason="TODO")
    def test_reward_notification_when_block_is_fully_validated(self):
        """
        On login:
        ✅ If a block has been validated by three nodes and a reward exists for the user,
        notify the miner about the pending/received reward.
        """
        pass

    @pytest.mark.skip(reason="TODO")
    def test_notify_user_of_new_blocks_added_since_last_login(self):
        """
        On login:
        ✅ Show newly added blocks since user's previous session,
        including whether they are confirmed or awaiting validation.
        """
        pass

    @pytest.mark.skip(reason="TODO")
    def test_notify_rejected_transactions_of_user(self):
        """
        On login:
        ✅ User must see any of their own rejected transactions.
        """
        pass

    @pytest.mark.skip(reason="TODO")
    def test_notify_successful_transactions_of_user(self):
        """
        On login:
        ✅ User must see successful outgoing/incoming transactions since last session.
        """
        pass

    @pytest.mark.skip(reason="TODO")
    def test_flagged_invalid_transactions_are_canceled_and_notified(self):
        """
        On login:
        ✅ Flagged (invalid) transactions created by the user must be auto-canceled
        and user must be notified.
        """
        pass

    @pytest.mark.skip(reason="TODO")
    def test_notification_history_is_cleared_only_after_user_reads_it(self):
        """
        On login:
        ✅ Notifications should only be marked as read/cleared after they are displayed to the user.
        """
        pass

    @pytest.mark.skip(reason="TODO")
    def test_notifications_are_filtered_only_to_users_relevant_events(self):
        """
        On login:
        ✅ User must only see notifications related to them or to the global chain state
        and not irrelevant user-specific events.
        """
        pass


if __name__ == '__main__':
    unittest.main()
