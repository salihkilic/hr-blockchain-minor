from base.subscribable import Subscribable


class GenesisBlockAddedFromNetworkEvent(Subscribable):
    @classmethod
    def dispatch(cls):
        cls._call_subscribers(None)