"""
MiniMax Speech API 配置
"""

import os
from typing import Optional


class APIConfig:
    """API配置类"""

    # API基础URL
    BASE_URL = "https://api.minimax.io/v1"

    # T2A API端点
    T2A_ENDPOINT = "/t2a_v2"
    GET_VOICE_LIST_ENDPOINT = "/get_voice"
    UPLOAD_ENDPOINT = "/files/upload"
    VOICE_CLONE_ENDPOINT = "/voice_clone"
    VOICE_DELETE_ENDPOINT = "/delete_voice"

    # 默认超时时间（秒）
    DEFAULT_TIMEOUT = 30

    # 最大重试次数
    MAX_RETRIES = 3

    # 重试延迟（秒）
    RETRY_DELAY = 1

    def __init__(
        self,
        api_key: Optional[str] = None,
        group_id: Optional[str] = None,
        base_url: Optional[str] = None,
        timeout: Optional[int] = None,
        max_retries: Optional[int] = None,
    ):
        self.api_key = api_key or self._get_api_key_from_env()
        self.group_id = group_id or self._get_group_id_from_env()
        self.base_url = base_url or self.BASE_URL
        self.timeout = timeout or self.DEFAULT_TIMEOUT
        self.max_retries = max_retries or self.MAX_RETRIES

        if not self.api_key:
            raise ValueError(
                "API key is required. Set MINIMAX_API_KEY environment variable or pass api_key parameter."
            )
        if not self.group_id:
            raise ValueError(
                "GroupId is required. Set MINIMAX_GROUP_ID environment variable or pass api_key parameter."
            )

    @property
    def t2a_url(self) -> str:
        return f"{self.base_url}{self.T2A_ENDPOINT}?GroupId={self.group_id}"

    @property
    def voice_list_url(self) -> str:
        return f"{self.base_url}{self.GET_VOICE_LIST_ENDPOINT}"

    @property
    def upload_url(self) -> str:
        return f"{self.base_url}{self.UPLOAD_ENDPOINT}?GroupId={self.group_id}"

    @property
    def voice_clone_url(self) -> str:
        return f"{self.base_url}{self.VOICE_CLONE_ENDPOINT}?GroupId={self.group_id}"

    @property
    def voice_delete_url(self) -> str:
        return f"{self.base_url}{self.VOICE_DELETE_ENDPOINT}?GroupId={self.group_id}"

    @staticmethod
    def _get_api_key_from_env() -> Optional[str]:
        """从环境变量获取API密钥"""
        return os.getenv("MINIMAX_API_KEY")

    @staticmethod
    def _get_group_id_from_env() -> Optional[str]:
        """从环境变量获取API密钥"""
        return os.getenv("MINIMAX_GROUP_ID")

    def get_headers(self) -> dict:
        """获取请求头"""
        return {
            "authority": "api.minimax.io",
            "Authorization": f"Bearer {self.api_key}",
        }


class VoiceConfig:
    """声音配置"""

    # 声音映射配置
    VOICE_MAPPING = {
        "male-zh": {
            "voice_id": "male-zh-1",
            "language": "zh",
            "description": "中文男声",
        },
        "female-zh": {
            "voice_id": "female-zh-1",
            "language": "zh",
            "description": "中文女声",
        },
        "male-en": {
            "voice_id": "male-en-1",
            "language": "en",
            "description": "英文男声",
        },
        "female-en": {
            "voice_id": "female-en-1",
            "language": "en",
            "description": "英文女声",
        },
        "male-fr": {
            "voice_id": "male-fr-1",
            "language": "fr",
            "description": "法文男声",
        },
        "female-fr": {
            "voice_id": "female-fr-1",
            "language": "fr",
            "description": "法文女声",
        },
        "male-ru": {
            "voice_id": "male-ru-1",
            "language": "ru",
            "description": "俄文男声",
        },
        "female-ru": {
            "voice_id": "female-ru-1",
            "language": "ru",
            "description": "俄文女声",
        },
    }

    @classmethod
    def get_voice_info(cls, voice_id: str) -> dict:
        """获取声音信息"""
        return cls.VOICE_MAPPING.get(voice_id, {})

    @classmethod
    def get_available_voices(cls) -> list:
        """获取所有可用的声音"""
        return list(cls.VOICE_MAPPING.keys())


class LanguageConfig:
    """语言配置"""

    # 语言映射
    LANGUAGE_MAPPING = {
        "zh": {"name": "Chinese", "native_name": "中文", "code": "zh-CN"},
        "en": {"name": "English", "native_name": "English", "code": "en-US"},
        "fr": {"name": "French", "native_name": "Français", "code": "fr-FR"},
        "ru": {"name": "Russian", "native_name": "Русский", "code": "ru-RU"},
    }

    @classmethod
    def get_language_info(cls, lang_code: str) -> dict:
        """获取语言信息"""
        return cls.LANGUAGE_MAPPING.get(lang_code, {})

    @classmethod
    def get_supported_languages(cls) -> list:
        """获取支持的语言列表"""
        return list(cls.LANGUAGE_MAPPING.keys())
