class InitializationService:

    @classmethod
    def initialize_application(cls):
        from services import FileSystemService
        filesystem_service = FileSystemService()
        filesystem_service.initialize_data_files()

        from repositories.user import UserRepository
        user_repository = UserRepository()
        user_repository.setup_database_structure()

        from blockchain import Pool
        Pool.get_instance()
        from blockchain import Ledger
        Ledger.get_instance()