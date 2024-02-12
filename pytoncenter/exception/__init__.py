class TonException(Exception):
    def __init__(self, code: int):
        self.code = code
