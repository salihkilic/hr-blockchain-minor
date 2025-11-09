from base.subscribable import Subscribable
from exceptions.user.invalid_credentials_exception import InvalidCredentialsException
from models import User
from repositories.user.user_repository import UserRepository

class UserService(Subscribable):

    logged_in_user: User | None = None

    def __init__(self):
        self.repo = UserRepository()

    def login(self, username:str, password:str) -> None:
        user = self.repo.find_by_username(username)

        if user is None:
            raise InvalidCredentialsException(field="username", message="Username does not exist.")

        if not user.verify_password(password):
            raise InvalidCredentialsException(field="password", message="Incorrect password.")

        self.__class__.logged_in_user = user
        self._call_subscribers(user)

    def logout(self) -> None:
        self.__class__.logged_in_user = None
        self.__class__._call_subscribers(None)

    def register(self, username:str, password:str) -> User:
        user = User.create(username, password)
        self.repo.persist(user)
        return user