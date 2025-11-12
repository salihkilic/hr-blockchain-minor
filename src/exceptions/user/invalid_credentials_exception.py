class InvalidCredentialsException(Exception):
    """Raised when attempting to create a user with an existing username."""

    field: str

    def __init__(self, field: str, message: str = "Invalid user data provided."):
        self.field = field
        super().__init__(message)