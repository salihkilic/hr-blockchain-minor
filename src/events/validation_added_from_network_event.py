import logging

from base.subscribable import Subscribable


class ValidationAddedFromNetworkEvent(Subscribable):
    @classmethod
    def dispatch(cls):
        cls._call_subscribers(None)