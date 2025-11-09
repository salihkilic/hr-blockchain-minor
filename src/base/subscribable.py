from abc import ABC


class Subscribable(ABC):

    def __init_subclass__(cls, **kwargs):
        super().__init_subclass__(**kwargs)
        cls._subscribers = set()

    @classmethod
    def _call_subscribers(cls, data):
        for callback in cls._subscribers:
            callback(data)

    @classmethod
    def subscribe(cls, callback):
        cls._subscribers.add(callback)
