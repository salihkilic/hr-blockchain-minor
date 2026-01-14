from base.subscribable import Subscribable


class TransactionAddedFromNetworkEvent(Subscribable):
    @classmethod
    def dispatch(cls):
        cls._call_subscribers(None)