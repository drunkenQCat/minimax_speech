"""
MiniMax Voice Clone API 数据模型
"""

from typing import Optional
from pydantic import BaseModel, Field

from .common_models import BaseResponse, ValidModels


class VoiceCloneRequest(BaseModel):
    """语音克隆请求模型"""

    file_id: int = Field(description="要克隆的文件ID，支持mp3、m4a、wav格式")
    voice_id: str = Field(
        description="自定义用户定义的ID，最少8个字符，必须包含字母和数字并以字母开头"
    )
    need_noise_reduction: Optional[bool] = Field(
        default=False, description="启用降噪，默认为false"
    )
    text: Optional[str] = Field(
        default=None,
        description="模型将为给定文本生成音频，用于预览语音克隆效果，限制2000字符",
    )
    model: Optional[ValidModels] = Field(
        default=None, description="指定用于预览的TTS模型"
    )
    accuracy: Optional[float] = Field(
        default=0.7, description="文本验证精度阈值，范围[0,1]"
    )
    need_volume_normalization: Optional[bool] = Field(
        default=False, description="是否启用音量标准化"
    )


class VoiceCloneResponse(BaseModel):
    """语音克隆响应模型"""

    input_sensitive: bool = Field(description="指示输入音频是否触发了任何错误")
    base_resp: BaseResponse = Field(description="基础响应信息")


class VoiceDeleteResponse(BaseModel):
    """语音删除响应模型"""

    voice_id: str = Field(description="已删除的语音ID")
    created_time: str = Field(description="已删除的语音创建时间")
    base_resp: BaseResponse = Field(description="基础响应信息")