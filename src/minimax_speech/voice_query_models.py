"""
MiniMax Voice API 数据模型
"""

from typing import Literal, Optional
from pydantic import BaseModel, Field

from .common_models import BaseResponse

VoiceType = Literal[
    "system",
    "voice_cloning",
    "voice_generation",
    "music_generation",
    "all",
]


class VoiceSlot(BaseModel):
    """语音槽位信息"""

    voice_id: str = Field(description="语音ID")
    voice_name: str = Field(description="语音名称")
    description: list[str] = Field(description="语音描述")


class SystemVoice(BaseModel):
    """系统语音信息"""

    voice_id: str = Field(description="语音ID")
    voice_name: str = Field(description="语音官方名称")
    description: list[str] = Field(description="语音描述")


class VoiceCloning(BaseModel):
    """克隆语音信息"""

    voice_id: str = Field(description="克隆语音的语音ID")
    description: list[str] = Field(description="语音描述")
    created_time: str = Field(description="语音生成时间戳 (yyyy-mm-dd)")


class VoiceGeneration(BaseModel):
    """语音生成信息"""

    voice_id: str = Field(description="设计语音的语音ID")
    description: list[str] = Field(description="语音描述")
    created_time: str = Field(description="语音生成时间戳 (yyyy-mm-dd)")


class MusicGeneration(BaseModel):
    """音乐生成信息"""

    voice_id: str = Field(description="歌曲的语音ID")
    instrumental_id: str = Field(description="歌曲的乐器ID")
    created_time: str = Field(description="语音生成时间戳 (yyyy-mm-dd)")


class VoiceListResponse(BaseModel):
    """语音列表响应"""

    voice_slots: Optional[list[VoiceSlot]] = Field(
        description="订阅语音计划期间创建的所有语音"
    )
    system_voice: Optional[list[SystemVoice]] = Field(description="所有可用的系统语音")
    voice_cloning: Optional[list[VoiceCloning]] = Field(description="账户下的所有克隆语音")
    voice_generation: Optional[list[VoiceGeneration]] = Field(
        description="通过语音设计API创建的所有语音"
    )
    music_generation: Optional[list[MusicGeneration]] = Field(
        description="通过音乐生成API创建的所有语音"
    )
    base_resp: BaseResponse = Field(..., description="基本响应信息")
