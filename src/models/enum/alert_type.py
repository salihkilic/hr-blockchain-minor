from enum import Enum

class AlertType(Enum):
    SUCCESS = 'success'
    WARNING = 'warning'
    INFO='info'
    DANGER='danger'