from base.subscribable import Subscribable


class BlockAddedFromNetworkEvent(Subscribable):
    @classmethod
    def dispatch(cls):
        cls._call_subscribers(None)