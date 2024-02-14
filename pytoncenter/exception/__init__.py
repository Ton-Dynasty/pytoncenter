class TonException(Exception):
    def __init__(self, code: int):
        self.code = code


class TonCenterException(Exception):
    def __init__(self, code: int, msg: str):
        super().__init__(msg)
        self.code = code
        self.msg = msg

    def __str__(self):
        return f"\033[93mTonCenterException {self.code}: {self.msg}\033[0m"


class TonCenterValidationException(Exception):
    def __init__(self, code: int, msg):
        super().__init__(msg)
        self.code = code
        self.msg = msg

    def __str__(self):
        return f"\033[93mTonCenterValidationException {self.code}: {self.msg}\033[0m"
