DEBUG = True


class NoUserFoundError(Exception):

    @property
    def error_message(self):
        if DEBUG and self.args:
            return f"User with id={self.args[0]} not found"
        else:
            return "User not found"
