"""
MiniMax Speech API 数据模型
"""

from enum import Enum
from typing import Literal, Optional

from pydantic import BaseModel, Field, confloat, conint

from .common_models import BaseResponse, ValidSr, ValidBitRate, ValidAudioFormat, ValidModels


class Language(str, Enum):
    """支持的语言"""

    CHINESE = "Chinese"
    CHINESE_YUE = "Chinese,Yue"
    ENGLISH = "English"
    ARABIC = "Arabic"
    RUSSIAN = "Russian"
    SPANISH = "Spanish"
    FRENCH = "French"
    PORTUGUESE = "Portuguese"
    GERMAN = "German"
    TURKISH = "Turkish"
    DUTCH = "Dutch"
    UKRAINIAN = "Ukrainian"
    VIETNAMESE = "Vietnamese"
    INDONESIAN = "Indonesian"
    JAPANESE = "Japanese"
    ITALIAN = "Italian"
    KOREAN = "Korean"
    THAI = "Thai"
    POLISH = "Polish"
    ROMANIAN = "Romanian"
    GREEK = "Greek"
    CZECH = "Czech"
    FINNISH = "Finnish"
    HINDI = "Hindi"
    AUTO = "auto"


class Voice(str, Enum):
    """支持的声音类型"""

    # 智慧女性
    WISE_WOMAN = "Wise_Woman"
    # 友好人士
    FRIENDLY_PERSON = "Friendly_Person"
    # 励志女孩
    INSPIRATIONAL_GIRL = "Inspirational_girl"
    # 深沉男声
    DEEP_VOICE_MAN = "Deep_Voice_Man"
    # 平静女性
    CALM_WOMAN = "Calm_Woman"
    # 随性男士
    CASUAL_GUY = "Casual_Guy"
    # 活泼女孩
    LIVELY_GIRL = "Lively_Girl"
    # 耐心男士
    PATIENT_MAN = "Patient_Man"
    # 年轻骑士
    YOUNG_KNIGHT = "Young_Knight"
    # 坚定男士
    DETERMINED_MAN = "Determined_Man"
    # 可爱女孩
    LOVELY_GIRL = "Lovely_Girl"
    # 体面男孩
    DECENT_BOY = "Decent_Boy"
    # 威严仪态
    IMPOSING_MANNER = "Imposing_Manner"
    # 优雅男士
    ELEGANT_MAN = "Elegant_Man"
    # 女修道院长
    ABBESS = "Abbess"
    # 甜美女孩2
    SWEET_GIRL_2 = "Sweet_Girl_2"
    # 热情女孩
    EXUBERANT_GIRL = "Exuberant_Girl"


class AudioChannels(int, Enum):
    MONO = 1
    STEREO = 2


class VoiceSetting(BaseModel):
    speed: confloat(ge=0.5, le=2) = 1.0  # type: ignore[reportInvalidTypeForm]
    vol: confloat(gt=0, le=10) = 1.0  # type: ignore[reportInvalidTypeForm]
    pitch: conint(ge=-12, le=12) = 0  # type: ignore[reportInvalidTypeForm]
    voice_id: Optional[str | Voice] = None
    emotion: Optional[
        Literal["happy", "sad", "angry", "fearful", "disgusted", "surprised", "neutral"]
    ] = None
    english_normalization: bool = False


class AudioSetting(BaseModel):
    sample_rate: Optional[ValidSr] = 32000
    bitrate: Optional[ValidBitRate] = 128000
    format: Optional[ValidAudioFormat] = "mp3"
    channel: AudioChannels = AudioChannels.MONO

    class AudioSetting:
        use_enum_values = True


class PronunciationDict(BaseModel):
    tone: Optional[list[str]] = None


class TimberWeight(BaseModel):
    voice_id: str
    weight: conint(ge=1, le=100)  # type: ignore[reportInvalidTypeForm]


class T2ARequest(BaseModel):
    model: ValidModels
    text: str = Field(..., max_length=5000)
    voice_setting: VoiceSetting
    audio_setting: AudioSetting = AudioSetting()
    pronunciation_dict: Optional[PronunciationDict] = None
    timber_weights: Optional[list[TimberWeight]] = None
    stream: bool = False
    language_boost: Optional[Language] = None
    subtitle_enable: bool = False
    output_format: Literal["url", "hex"] = "hex"


class T2AData(BaseModel):
    """文本转语音响应模型"""

    audio: bytes = Field(..., description="音频数据")
    status: int = Field(
        1,
        description="目前生成状态码。1代表现在音频流正在生成，2代表音频流已经生成完成",
    )
    ced: Optional[str] = Field(..., description="不知道啥")


class ErrorResponse(BaseModel):
    """错误响应模型"""

    error_code: str = Field(..., description="错误代码")
    error_message: str = Field(..., description="错误信息")
    request_id: Optional[str] = Field(None, description="请求ID")


class APIStatus(str, Enum):
    """API状态"""

    SUCCESS = "success"
    ERROR = "error"
    PROCESSING = "processing"


class T2AExtra(BaseModel):
    """T2A额外信息"""

    audio_length: int = Field(..., description="音频长度（毫秒）")
    audio_sample_rate: int = Field(24000, description="采样率，默认24000")
    audio_size: int = Field(..., description="生成的音频大小（字节）")
    audio_bitrate: int = Field(168000, description="比特率，默认168000")
    audio_format: Literal["mp3", "pcm", "flac"] = Field(
        ..., description="生成的音频格式"
    )
    audio_channel: int = Field(
        ..., ge=1, le=2, description="音频声道数，1:单声道 2:立体声"
    )
    invisible_character_ratio: float = Field(..., description="非法字符百分比")
    usage_characters: int = Field(..., description="本次语音生成的计费字符数")


class T2AResponse(BaseModel):
    """T2A状态响应模型"""

    data: T2AData = Field(..., description="处理结果")
    extra_info: T2AExtra = Field(..., description="额外信息")
    trace_id: str = Field(..., description="任务ID")
    base_resp: BaseResponse = Field(..., description="基础响应信息")
