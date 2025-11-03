from models import User
from repositories.user import AbstractUserRepository
from repositories.user.user_repository import UserRepository

class UserService:

    def __init__(self, user_repo: AbstractUserRepository = None):
        self.repo = user_repo if not None else UserRepository()

    def login(self, username:str, password:str) -> User | None:
        user = self.repo.find_by_username(username)
        if user and user.verify_password(password):
            return user
        return None