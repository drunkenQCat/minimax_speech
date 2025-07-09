"""
MiniMax Speech API 异常类
"""


class MiniMaxError(Exception):
    """MiniMax API 基础异常类"""

    pass


class MiniMaxAPIError(MiniMaxError):
    """API调用异常"""

    def __init__(
        self,
        message: str,
        status_code: int | None = None,
        response_data: dict | None = None,
    ):
        super().__init__(message)
        self.status_code = status_code
        self.response_data = response_data or {}


class MiniMaxTimeoutError(MiniMaxError):
    """超时异常"""

    pass


class MiniMaxValidationError(MiniMaxError):
    """参数验证异常"""

    pass


class MiniMaxAuthenticationError(MiniMaxAPIError):
    """认证异常"""

    pass


class MiniMaxRateLimitError(MiniMaxAPIError):
    """速率限制异常"""

    pass


class MiniMaxQuotaExceededError(MiniMaxAPIError):
    """配额超限异常"""

    pass

