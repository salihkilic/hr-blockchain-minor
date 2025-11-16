import os

from blockchain import Ledger, Pool
from exceptions.user import DuplicateUsernameException
from models import User, Transaction, Block
from models.block import BlockStatus
from repositories.user import UserRepository
from services import InitializationService, FileSystemService


def UserFixtures():
    init_service = InitializationService()
    init_service.initialize_application()

    user_repo = UserRepository()

    users_to_create = [
        ("alice", "alicepw"),
        ("bob", "bobpw"),
        ("charlie", "charliepw"),
        ("dave", "davepw"),
        ("eve", "evepw"),
    ]

    created_users = []

    for username, password in users_to_create:
        try:
            user = User.create(username, password)
            user_repo.persist(user)
            created_users.append(user)
        except DuplicateUsernameException:
            raise Exception(f"User '{username}' already exists. Please clear the database before running fixtures.")


    signup_rewards = [Transaction.create_signup_reward(user.address) for user in created_users]

    for tx in signup_rewards:
        Pool.get_instance().add_transaction(tx)

if __name__ == "__main__":
    UserFixtures()