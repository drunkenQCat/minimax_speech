"""
MiniMax Speech API Python 包

一个基于MiniMax API的Python语音处理包，支持文本转语音(T2A)功能。
"""

__version__ = "0.1.0"
__author__ = "drunkenQCat"
__email__ = "songjh123123@outlook.com"

# 导出主要类
from .client import MiniMaxSpeech
from .async_client import AsyncMiniMaxSpeech
from .tts_models import (
    T2ARequest,
    T2AData,
    T2AResponse,
    VoiceSetting,
    AudioSetting,
    Language,
    Voice,
    BaseResponse,
    T2AExtra,
    PronunciationDict,
    TimberWeight
)
from .voice_query_models import (
    VoiceListResponse,
    VoiceSlot,
    SystemVoice,
    VoiceCloning,
    VoiceGeneration,
    MusicGeneration,
    VoiceType
)
from .file_upload_models import (
    FileUploadResponse,
    FileInfo
)
from .voice_clone_models import (
    VoiceCloneRequest,
    VoiceCloneResponse
)
from .config import VoiceConfig, LanguageConfig
from .exceptions import (
    MiniMaxError,
    MiniMaxAPIError,
    MiniMaxTimeoutError,
    MiniMaxValidationError,
    MiniMaxAuthenticationError,
    MiniMaxRateLimitError,
    MiniMaxQuotaExceededError,
)

__all__ = [
    # 客户端
    "MiniMaxSpeech",
    "AsyncMiniMaxSpeech",
    
    # 模型
    "T2ARequest",
    "T2AData",
    "T2AResponse",
    "VoiceSetting",
    "AudioSetting",
    "Language",
    "Voice",
    "BaseResponse",
    "T2AExtra",
    "PronunciationDict",
    "TimberWeight",
    
    # 语音列表模型
    "VoiceListResponse",
    "VoiceSlot",
    "SystemVoice",
    "VoiceCloning",
    "VoiceGeneration",
    "MusicGeneration",
    "VoiceType",
    
    # 文件上传模型
    "FileUploadResponse",
    "FileInfo",
    
    # 语音克隆模型
    "VoiceCloneRequest",
    "VoiceCloneResponse",
    
    # 配置
    "VoiceConfig",
    "LanguageConfig",
    
    # 异常
    "MiniMaxError",
    "MiniMaxAPIError",
    "MiniMaxTimeoutError",
    "MiniMaxValidationError",
    "MiniMaxAuthenticationError",
    "MiniMaxRateLimitError",
    "MiniMaxQuotaExceededError",
    
    # 元数据
    "__version__",
    "__author__",
    "__email__",
]


def main() -> None:
    print("Hello from minimax-speech!")
