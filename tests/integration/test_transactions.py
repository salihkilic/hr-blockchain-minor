import os
import tempfile
import unittest
from decimal import Decimal, ROUND_DOWN
from unittest.mock import patch

import pytest

from models import Transaction, User
from models.constants import FilesAndDirectories
from repositories.user import UserRepository
from services import FileSystemService, InitializationService


class TestTransactions(unittest.TestCase):

    @patch("services.filesystem_service.FileSystemService.get_data_root",
           side_effect=FileSystemService.get_temp_data_root)
    def setUp(self, mock_get_data_root):
        FileSystemService.clear_temp_data_root()
        InitializationService.initialize_application()

    @pytest.mark.integration
    @patch("services.filesystem_service.FileSystemService.get_data_root",
           side_effect=FileSystemService.get_temp_data_root)
    def test_transaction_can_have_fee_value(self, mock_get_data_root):
        """
        An extra value could be placed on a transaction as transaction fee.
        """
        user1 = User.create("tom", "geheim")
        user2 = User.create("salih", "geheim")

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
