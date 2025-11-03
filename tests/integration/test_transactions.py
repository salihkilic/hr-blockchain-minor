import os
import tempfile
import unittest
from decimal import Decimal, ROUND_DOWN

import pytest

from models import Transaction, User
from repositories.user import UserRepository
from services import FileSystemService


class TestTransactions(unittest.TestCase):

    def setUp(self):
        """ Set up the test environment before each test case. """
        tmp_path = tempfile.TemporaryDirectory().name
        db_path = os.path.join(tmp_path, FileSystemService.DATA_DIR_NAME, FileSystemService.USERS_DB_FILE_NAME)

        # Create folders
        os.makedirs(os.path.dirname(db_path), exist_ok=True)

        # Create the empty DB file
        open(db_path, 'a').close()

        user_repository = UserRepository(db_file_path=db_path)
        user_repository.setup_database_structure()
        self.user_repository = user_repository
        self.db_path = db_path

    @pytest.mark.integration
    def test_transaction_can_have_fee_value(self):
        """
        An extra value could be placed on a transaction as transaction fee.
        """
        user1 = User.create("tom", "geheim", user_db_path=self.db_path)
        user2 = User.create("salih", "geheim", user_db_path=self.db_path)

        tx_without_fee = Transaction.create(user1, user2.address, Decimal(10.0), fee=Decimal(0))

        assert tx_without_fee.fee == Decimal(0).quantize(Decimal("0.00000001"), rounding=ROUND_DOWN)

        tx_with_fee = Transaction.create(user1, user2.address, Decimal(10.0), fee=Decimal(0.1))

        assert tx_with_fee.fee == Decimal(0.1).quantize(Decimal("0.00000001"), rounding=ROUND_DOWN)


    @pytest.mark.skip(reason="Needs to be moved to E2E tests")
    def test_sender_must_enter_transaction_fee(self):
        """
        A sender must enter the transaction fee while creating a transaction.
        """
        pass


    if __name__ == '__main__':
        unittest.main()
