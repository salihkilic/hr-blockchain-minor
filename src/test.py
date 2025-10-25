
from repositories.user import UserRepository

if __name__ == "__main__":
    user_repository = UserRepository()
    user_repository.setup_database_structure()
