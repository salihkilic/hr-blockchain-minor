import unittest

import pytest


class UserRegistration(unittest.TestCase):

    @pytest.mark.skip(reason="TODO")
    def test_validation_of_unique_username(self):
        """ A user must provide a unique username and a password when registering in the system. """
        pass

    @pytest.mark.skip(reason="TODO")
    def test_validation_of_required_user_fields(self):
        """ A user must provide a unique username and a password when registering in the system. """
        pass

    @pytest.mark.skip(reason="TODO")
    def test_signup_reward(self):
        """ A node user will receive 50 coins as a sign-up reward, after registration. """
        pass

    @pytest.mark.skip(reason="TODO")
    def test_key_creation_on_signup(self):
        """ A unique pair of private key and public key must be created for a node user, after registration. """
        pass


if __name__ == '__main__':
    unittest.main()
