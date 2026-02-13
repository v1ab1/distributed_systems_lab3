class UserNotFoundError(Exception):
    def __init__(self, username: str):
        message = f"User with username={username} not found"
        super().__init__(message)
        self.username = username
        self.message = message


class UsernameAlreadyExistError(Exception):
    def __init__(self, username: str):
        message = f"User with username={username} already exist"
        super().__init__(message)
        self.username = username
        self.message = message
