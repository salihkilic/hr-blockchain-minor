from Models.Enum import TransactionType


class Transaction:

    def __init__(self, tx_id: str, sender: str, receiver: str, amount: float, tx_type: TransactionType):
        self.tx_id = tx_id
        self.sender = sender
        self.receiver = receiver
        self.amount = amount
        self.tx_type = tx_type