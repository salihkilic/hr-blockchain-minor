import logging

from exceptions.user import DuplicateUsernameException
from models import User
from repositories.user import AbstractUserRepository
from repositories.user.user_repository import UserRepository

class UserService:

    def __init__(self, user_repo: AbstractUserRepository = None):
        self.repo = user_repo if not None else UserRepository()
        self.logger = logging.getLogger(__name__)

    def get_user(self, username) -> User:
        return self.repo.find_by_username(username)

    def login(self, username:str, password:str) -> User | None:
        user = self.repo.find_by_username(username)
        if user and user.verify_password(password):
            return user
        return None

    def create_user(self, username:str, password:str) -> User | None:
        # Validate input
        if not self.validate_username(username) or not self.validate_password(password):
            return None
        # Create and persist user
        try:
            new_user = User.create(
                username=username,
                password=password)
            self.repo.persist(new_user)
            return new_user
        except DuplicateUsernameException:
            self.logger.exception(f"Username '{username}' already exists.")
        except Exception as e:
            self.logger.exception(f"Unexpected error during user creation: {e}")

    def update_user(self, user:User) -> bool:
        if not user or not user.username:
            self.logger.error("User or Username is missing for update")
            return False

        if not self.repo.username_exists(user.username):
            self.logger.error("User does not exist for update")
            return False

        self.repo.update(user)
        return True

    def delete_user(self, user:User):
        if not user:
            self.logger.error("User can't be null for deletion")
            return
        if not user.username:
            self.logger.error("Username can't be null for deletion")
            return
        if not self.repo.find_by_username(user.username):
            self.logger.error("User not found for deletion")
            return

        self.repo.delete(user)

    def validate_username(self, username: str) -> bool:
        # Not empty
        if not username:
            self.logger.error("Username cannot be empty")
            return False
        # Unique
        if self.repo.username_exists(username):
            self.logger.error("Username must be unique")
            return False
        # Length constraints
        if len(username) < 3 or len(username) > 30:
            self.logger.error("Username must be between 3 and 30 characters")
            return False

        return True

    def validate_password(self, password: str) -> bool:
        # Not empty
        if not password:
            self.logger.error("Password can't be empty")
            return False

        # Length constraints
        if len(password) < 5 or len(password) > 20:
            self.logger.error("Password must be between 5 and 20 characters")
            return False

        return True