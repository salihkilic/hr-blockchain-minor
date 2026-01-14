class CatchupService:

    def request_block_catchup(self, after_number: int) -> None:
        from services.networking_service import NetworkingService
        NetworkingService.get_instance().request_next_block(after_number=after_number)

    def request_pool_catchup(self) -> None:
        from services.networking_service import NetworkingService
        NetworkingService.get_instance().request_pool_snapshot()

    def request_validation_catchup(self) -> None:
        from services.networking_service import NetworkingService
        NetworkingService.get_instance().request_validation_snapshot()

    def volunteer_block_catchup(self) -> None:
        from blockchain import Ledger
        Ledger.get_instance().handle_network_sync_request({
            "after_number": -1,
        })

    def volunteer_pool_catchup(self) -> None:
        from blockchain import Pool
        Pool.get_instance().handle_network_pool_sync_request({})

    def volunteer_validation_catchup(self) -> None:
        from blockchain import Ledger
        Ledger.get_instance().handle_validation_sync_request({})