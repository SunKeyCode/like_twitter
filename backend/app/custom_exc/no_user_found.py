from configs.app_config import DEBUG


class NoUserFoundError(Exception):

    @property
    def error_message(self) -> str:
        if DEBUG and self.args:
            return f"User with id={self.args[0]} not found"
        else:
            return "User not found"
