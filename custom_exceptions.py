from sqlalchemy.exc import IntegrityError


class DbIntegrityError(Exception):

    def __int__(self, message):
        self.message = message
        self.process_error_message()

    def process_error_message(self):
        print(self.message)
