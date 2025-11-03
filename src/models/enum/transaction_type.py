from enum import Enum

class TransactionType(Enum):
    TRANSFER = 'transfer'
    SIGNUP_REWARD = 'signup reward'
    MINING_REWARD = 'mining reward'