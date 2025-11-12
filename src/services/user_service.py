from base.subscribable import Subscribable
from exceptions.user.invalid_credentials_exception import InvalidCredentialsException
from models import User, Transaction
from repositories.user.user_repository import UserRepository

class UserService(Subscribable):

    logged_in_user: User | None = None

    def __init__(self):
        self.repo = UserRepository()
        # Ensure database schema exists for tests and runtime
        try:
            self.repo.setup_database_structure()
        except Exception:
            # If initialization fails, proceed; operations will raise cleanly
            pass

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

    def register(self, username:str, password:str) -> None:
        user = User.create(username, password)
        self.repo.persist(user)

        signup_reward = Transaction.create_signup_reward(user.address)
        from blockchain import Pool
        Pool.get_instance().add_transaction(signup_reward)