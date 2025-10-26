import unittest

import pytest


class MyTestCase(unittest.TestCase):

    @pytest.mark.skip(reason="TODO")
    def test_sha256_is_used_for_hashing(self):
        """
        SHA256 must be used for any hashing in the system.
        """
        pass

    @pytest.mark.skip(reason="TODO")
    def test_password_is_stored_as_hash(self):
        """
        A password must be saved in the form of a hash in the system.
        """
        pass

    @pytest.mark.skip(reason="TODO")
    def test_user_can_view_private_and_public_key_when_logged_in(self):
        """
        A user must be able to see their private key and public key when logged in.
        """
        pass

    @pytest.mark.skip(reason="TODO")
    def test_username_or_hashed_public_key_is_used_as_account_number(self):
        """
        A username (or hashed unique public key) must be used as the public account number of a user for any transaction.
        """
        pass


if __name__ == '__main__':
    unittest.main()
