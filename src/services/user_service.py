from exceptions.user.invalid_credentials_exception import InvalidCredentialsException
from models import User
from repositories.user import AbstractUserRepository
from repositories.user.user_repository import UserRepository

class UserService:

    _subscribers = set()
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

        for callback in self.__class__._subscribers:
            callback(user)

    def logout(self) -> None:
        self.__class__.logged_in_user = None

        for callback in self.__class__._subscribers:
            callback(None)

    def register(self, username:str, password:str) -> User:
        user = User.create(username, password)
        self.repo.persist(user)
        return user

    @classmethod
    def subscribe(cls, callback):
        cls._subscribers.add(callback)
