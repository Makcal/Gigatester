class MyException(Exception):
    pass


class MyContainerError(MyException):
    def __init__(self, message):
        self.message = message
