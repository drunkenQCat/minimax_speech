"""MiniMax Voice Design API 数据模型"""

from pydantic import BaseModel, Field

from .common_models import BaseResponse, ValidModels


class VoiceDesignRequest(BaseModel):
    """语音克隆请求模型"""

    prompt: str = Field(
        description="自定义用户定义的ID，最少8个字符，必须包含字母和数字并以字母开头"
    )
    preview_text: str = Field(
        default="你好，这是一条测试音频。Hello, this is a test audio",
        description="模型将为给定文本生成音频，用于预览语音克隆效果，限制2000字符",
    )
    voice_id: str = Field(
        description="自定义用户定义的ID，最少8个字符，必须包含字母和数字并以字母开头"
    )


class VoiceDesignResponse(BaseModel):
    """语音克隆响应模型"""

    voice_id: str = Field(
        description="自定义用户定义的ID，最少8个字符，必须包含字母和数字并以字母开头"
    )
    trial_audio: str = Field(description="预览用语音，使用十六位编码格式")
    input_sensitive: bool = Field(description="指示输入音频是否触发了任何错误")
    base_resp: BaseResponse = Field(description="基础响应信息")
