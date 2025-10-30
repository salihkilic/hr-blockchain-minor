from models.enum import AlertType


class UIAlert:

    def __init__(self, title: str, message: str, alert_type: AlertType):
        self.title = title
        self.message = message
        self.alert_type = alert_type