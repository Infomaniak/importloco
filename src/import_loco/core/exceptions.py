class LocoError(Exception):
    pass


class LocoConfigError(LocoError):
    pass


class LocoNetworkError(LocoError):
    pass


class LocoParserError(LocoError):
    pass


class LocoValidationError(LocoError):
    pass
