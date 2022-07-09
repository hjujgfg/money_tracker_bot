class LogicalError(Exception):
    pass


class NoWalletException(LogicalError):
    pass


class NoCapsulesException(LogicalError):
    pass


class NoSuchCurrencyException(LogicalError):
    pass


class NoSuchCapsuleExcpetion(LogicalError):
    pass
