import unittest
from decimal import Decimal
from unittest.mock import patch

from models import User, Transaction
from models.enum import TransactionType
from services import FileSystemService, InitializationService


class TestTransactionModel(unittest.TestCase):

    @patch("services.filesystem_service.FileSystemService.get_data_root",
           side_effect=FileSystemService.get_temp_data_root)
    def setUp(self, mock_get_data_root):
        FileSystemService.clear_temp_data_root()
        InitializationService.initialize_application()

    @patch("services.filesystem_service.FileSystemService.get_data_root",
           side_effect=FileSystemService.get_temp_data_root)
    def test_create_mining_reward(self, mock_get_data_root):
        user1 = User.create("node1", "password")
        user2 = User.create("node2", "password")
        user3 = User.create("node3", "password")
        user4 = User.create("node4", "password")

        transactions_to_be_mined = [
            Transaction.create(
                sender=user1,
                receiver_address=user2.address,
                amount=Decimal('10.0'),
                fee=Decimal('0.1')
            ),
            Transaction.create(
                sender=user2,
                receiver_address=user3.address,
                amount=Decimal('20.0'),
                fee=Decimal('0.2')
            ),
            Transaction.create(
                sender=user3,
                receiver_address=user4.address,
                amount=Decimal('30.0'),
                fee=Decimal('0.3')
            ),
            Transaction.create(
                sender=user4,
                receiver_address=user1.address,
                amount=Decimal('40.0'),
                fee=Decimal('0.4')
            ),
            Transaction.create(
                sender=user1,
                receiver_address=user3.address,
                amount=Decimal('50.0'),
                fee=Decimal('0.5')
            ),
        ]

        reward_tx = Transaction.create_mining_reward(
            receiver_address=user1.address,
            transactions_to_be_mined=transactions_to_be_mined
        )

        assert reward_tx.receiver_address == user1.address
        assert reward_tx.amount == Decimal('51.5')
        assert reward_tx.fee == Decimal('0')
        assert reward_tx.kind == TransactionType.MINING_REWARD
