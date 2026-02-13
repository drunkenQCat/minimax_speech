from typing import Literal

from pydantic import BaseModel, Field

ValidSr = Literal[8000, 16000, 22050, 24000, 32000, 44100]
ValidBitRate = Literal[32000, 64000, 128000, 256000]
ValidAudioFormat = Literal["mp3", "pcm", "flac", "wav"]
ValidModels = Literal[
    "speech-2.8-hd",
    "speech-2.8-turbo",
    "speech-2.6-hd",
    "speech-2.6-turbo",
    # "speech-2.5-hd-preview",
    # "speech-2.5-turbo-preview",
    "speech-02-hd",
    "speech-02-turbo",
    "speech-01-hd",
    "speech-01-turbo",
]
ValidDeleteVoiceType = Literal["voice_generation", "voice_cloning"]
ValidEmotions = Literal[
    "happy",
    "sad",
    "angry",
    "fearful",
    "disgusted",
    "surprised",
    "calm",
    "fluent",
]


class BaseResponse(BaseModel):
    """基础响应模型"""

    status_code: int = Field(..., description="状态码")
    status_msg: str | None = Field(..., description="状态消息")

    @property
    def is_success(self) -> bool:
        """检查响应是否成功"""
        return self.status_msg == "success"

    @property
    def error_type(self) -> str:
        """获取错误类型描述"""
        error_mapping = {
            1000: "未知错误",
            1001: "超时",
            1002: "触发流量限制",
            1004: "认证失败",
            1039: "触发TPM流量限制",
            1042: "非法字符超过最大值（超过输入的10%）",
            2013: "输入格式无效",
            2038: "无克隆音色许可",
            2039: "音色ID已经存在",
        }
        error_msg = (
            error_mapping.get(self.status_code, "未知错误") + f": {self.status_msg}"
        )
        return error_msg
