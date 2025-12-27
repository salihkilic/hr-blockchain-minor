class AbstractSerializableModel:
    def to_dict(self):
        raise NotImplementedError("Subclasses must implement to_dict method")

    @classmethod
    def from_dict(cls, data):
        raise NotImplementedError("Subclasses must implement from_dict method")