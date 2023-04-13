import re


class DbIntegrityError(Exception):
    @property
    def error_message(self) -> str:
        if not self.args:
            return "No args for error message"
        try:
            # if config.DEBUG:
            #     return self.args[0][0]
            # else:
            return self._process_error_message(self.args[0][0])
        except IndexError:
            return "Error message failed"

    @staticmethod
    def _process_error_message(to_process: str) -> str:
        if not isinstance(to_process, str):
            return "No error message"

        result = re.search(pattern=r"(?<=DETAIL:  ).+", string=to_process)
        if result:
            return result[0]
        else:
            return "No error message"
