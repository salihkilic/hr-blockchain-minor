from Models import Transaction


class ITransactionRepository():

    def find_by_block_id(self, block_id: int) -> list[Transaction]:
        raise NotImplementedError

    def find_in_transaction_pool(self) -> list[Transaction]:
        raise NotImplementedError