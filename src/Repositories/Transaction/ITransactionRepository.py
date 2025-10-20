class ITransactionRepository():

    def find_by_block_id(self, block_id: int):
        raise NotImplementedError