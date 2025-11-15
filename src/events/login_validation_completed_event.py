from base.subscribable import Subscribable


class LoginValidationCompletedEvent(Subscribable):
    @classmethod
    def dispatch(cls):
        cls._call_subscribers(None)