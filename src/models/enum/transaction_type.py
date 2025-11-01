from enum import Enum

class TransactionType(Enum):
    TRANSFER = 'transfer'
    SIGNUP_REWARD = 'signup_reward'
    MINING_REWARD = 'mining_reward'