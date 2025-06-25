class APIError(RuntimeError):
    """对外统一抛出的业务异常。"""

__all__ = ["APIError"]
