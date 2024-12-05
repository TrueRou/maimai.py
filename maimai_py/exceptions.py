class MaimaiPyError(Exception):
    """
    Base exception class for all exceptions raised by maimai_py.
    """

    pass


class InvalidDeveloperTokenError(MaimaiPyError):
    """
    Raised when the developer token is not provided or token is invalid.

    Developed token should be provided in the constructor of the provider.
    """

    pass


class InvalidPlateError(MaimaiPyError):
    """
    Raised when the provided version or plate is invalid.

    Plate should be formatted as two/three characters (version + kind), e.g. "桃将", "舞舞舞"

    The following versions are valid:

    霸, 舞, 初, 真, 超, 檄, 橙, 晓, 桃, 樱, 紫, 堇, 白, 雪, 辉, 熊, 华, 爽, 煌, 星, 宙, 祭, 祝, 双, 宴.

    The following kinds are valid:

    将, 者, 極, 极, 舞舞, 神

    """

    pass
