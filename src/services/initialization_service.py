class InitializationService:

    @classmethod
    def initialize_application(cls, node_number: int = 1):
        from services import FileSystemService, NodeFileSystemService
        if NodeFileSystemService._node_data_directory is None:
            NodeFileSystemService.set_node_data_directory_by_number(node_number)
        filesystem_service = FileSystemService()
        filesystem_service.initialize_data_files()
        node_filesystem_service = NodeFileSystemService()
        node_filesystem_service.initialize_data_files()

        filesystems_services = [filesystem_service, node_filesystem_service]

        for fss in filesystems_services:
            if not fss.hash_store_exists():
                if not fss.can_hash_store_be_initialized():
                    cls.exit_with_error_message(f"In {fss.__class__.get_name().lower()} hash store cannot be initialized because of existing data files. The system cannot verify integrity.")
                fss.initialize_hash_store()
            else:
                results = fss.verify_all_data_files()
                one_or_more_failures = any(not results[file]['ok'] for file in results)
                if one_or_more_failures:
                    reasons = [f"{file}: {results[file]['reason']}" for file in results if not results[file]['ok']]
                    cls.exit_with_error_message(f"In {fss.__class__.get_name().lower()} data file integrity verification failed:\n" + "\n".join(reasons))

        from repositories.user import UserRepository
        user_repository = UserRepository()
        user_repository.setup_database_structure()

        from services import NetworkingService
        NetworkingService.get_instance().configure(
            port=5555 if node_number == 1 else 5556,
            peer_addresses=[ "localhost:5556" if node_number == 1 else "localhost:5555" ],
        )
        NetworkingService.get_instance().start()

        NetworkingService.get_instance().register_handler(
            NetworkingService.TX_BROADCAST_TOPIC,
            lambda payload, _: Pool.get_instance().handle_network_transaction(payload)
        )

        NetworkingService.get_instance().register_handler(
            NetworkingService.BLOCK_BROADCAST_TOPIC,
            lambda payload, _: Ledger.get_instance().handle_network_block(payload)
        )

        NetworkingService.get_instance().register_handler(
            NetworkingService.VALIDATION_BROADCAST_TOPIC,
            lambda payload, _: Ledger.get_instance().handle_network_validation(payload)
        )

        from blockchain import Pool
        Pool.get_instance()
        from blockchain import Ledger
        Ledger.get_instance()

    @classmethod
    def exit_with_error_message(cls, message: str):
        print(f"\n\033[91m{message}\033[0m\n")
        raise RuntimeError(message)
