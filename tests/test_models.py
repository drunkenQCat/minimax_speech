"""
测试数据模型
"""

import pytest
from minimax_speech.tts_models import (
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


class TestLanguage:
    """测试语言枚举"""
    
    def test_language_values(self):
        """测试语言值"""
        assert Language.CHINESE.value == "Chinese"
        assert Language.ENGLISH.value == "English"
        assert Language.FRENCH.value == "French"
        assert Language.RUSSIAN.value == "Russian"
        assert Language.AUTO.value == "auto"


class TestVoice:
    """测试声音枚举"""
    
    def test_voice_values(self):
        """测试声音值"""
        assert Voice.WISE_WOMAN.value == "Wise_Woman"
        assert Voice.FRIENDLY_PERSON.value == "Friendly_Person"
        assert Voice.GRINCH.value == "Grinch"


class TestVoiceSetting:
    """测试声音设置"""
    
    def test_valid_voice_setting(self):
        """测试有效的声音设置"""
        voice_setting = VoiceSetting(
            voice_id="Wise_Woman",
            speed=1.0,
            vol=1.0,
            pitch=0
        )
        
        assert voice_setting.voice_id == "Wise_Woman"
        assert voice_setting.speed == 1.0
        assert voice_setting.vol == 1.0
        assert voice_setting.pitch == 0
        assert voice_setting.emotion is None
    
    def test_voice_setting_with_emotion(self):
        """测试带情感的声音设置"""
        voice_setting = VoiceSetting(
            voice_id="Grinch",
            speed=1.2,
            vol=0.8,
            pitch=2,
            emotion="happy"
        )
        
        assert voice_setting.emotion == "happy"
    
    def test_invalid_speed(self):
        """测试无效语速"""
        with pytest.raises(ValueError):
            VoiceSetting(
                voice_id="Wise_Woman",
                speed=3.0,  # 超出范围
                vol=1.0,
                pitch=0
            )
    
    def test_invalid_volume(self):
        """测试无效音量"""
        with pytest.raises(ValueError):
            VoiceSetting(
                voice_id="Wise_Woman",
                speed=1.0,
                vol=11.0,  # 超出范围
                pitch=0
            )
    
    def test_invalid_pitch(self):
        """测试无效音调"""
        with pytest.raises(ValueError):
            VoiceSetting(
                voice_id="Wise_Woman",
                speed=1.0,
                vol=1.0,
                pitch=15  # 超出范围
            )


class TestAudioSetting:
    """测试音频设置"""
    
    def test_valid_audio_setting(self):
        """测试有效的音频设置"""
        audio_setting = AudioSetting(
            sample_rate=32000,
            bitrate=128000,
            format="mp3",
            channel=1
        )
        
        assert audio_setting.sample_rate == 32000
        assert audio_setting.bitrate == 128000
        assert audio_setting.format == "mp3"
        assert audio_setting.channel == 1
    
    def test_invalid_sample_rate(self):
        """测试无效采样率"""
        with pytest.raises(ValueError):
            AudioSetting(
                sample_rate=48000,  # 无效值
                bitrate=128000,
                format="mp3"
            )
    
    def test_invalid_bitrate(self):
        """测试无效比特率"""
        with pytest.raises(ValueError):
            AudioSetting(
                sample_rate=32000,
                bitrate=512000,  # 无效值
                format="mp3"
            )
    
    def test_invalid_format(self):
        """测试无效格式"""
        with pytest.raises(ValueError):
            AudioSetting(
                sample_rate=32000,
                bitrate=128000,
                format="ogg"  # 无效格式
            )


class TestT2ARequest:
    """测试T2A请求模型"""
    
    def test_valid_request(self):
        """测试有效请求"""
        voice_setting = VoiceSetting(
            voice_id="Wise_Woman",
            speed=1.0,
            vol=1.0,
            pitch=0
        )
        
        audio_setting = AudioSetting(
            sample_rate=32000,
            bitrate=128000,
            format="mp3"
        )
        
        request = T2ARequest(
            model="speech-02-hd",
            text="Hello, world!",
            voice_setting=voice_setting,
            audio_setting=audio_setting
        )
        
        assert request.model == "speech-02-hd"
        assert request.text == "Hello, world!"
        assert request.voice_setting == voice_setting
        assert request.audio_setting == audio_setting
        assert request.stream is False
        assert request.output_format == "hex"
    
    def test_invalid_model(self):
        """测试无效模型"""
        voice_setting = VoiceSetting(voice_id="Wise_Woman")
        audio_setting = AudioSetting()
        
        with pytest.raises(ValueError):
            T2ARequest(
                model="invalid-model",
                text="Test",
                voice_setting=voice_setting,
                audio_setting=audio_setting
            )
    
    def test_text_too_long(self):
        """测试文本过长"""
        voice_setting = VoiceSetting(voice_id="Wise_Woman")
        audio_setting = AudioSetting()
        
        long_text = "a" * 6000  # 超过5000字符
        
        with pytest.raises(ValueError):
            T2ARequest(
                model="speech-02-hd",
                text=long_text,
                voice_setting=voice_setting,
                audio_setting=audio_setting
            )


class TestT2AData:
    """测试T2A数据模型"""
    
    def test_valid_data(self):
        """测试有效数据"""
        data = T2AData(
            audio="48656c6c6f",  # hex编码的音频数据
            status=2,
            subtitle_file="https://example.com/subtitle.srt"
        )
        
        assert data.audio == "48656c6c6f"
        assert data.status == 2
        assert data.subtitle_file == "https://example.com/subtitle.srt"


class TestT2AExtra:
    """测试T2A额外信息"""
    
    def test_valid_extra_info(self):
        """测试有效的额外信息"""
        extra = T2AExtra(
            audio_length=5000,
            audio_sample_rate=32000,
            audio_size=100000,
            audio_bitrate=128000,
            audio_format="mp3",
            audio_channel=1,
            invisible_character_ratio=0.0,
            usage_characters=100
        )
        
        assert extra.audio_length == 5000
        assert extra.audio_sample_rate == 32000
        assert extra.audio_size == 100000
        assert extra.audio_bitrate == 128000
        assert extra.audio_format == "mp3"
        assert extra.audio_channel == 1
        assert extra.invisible_character_ratio == 0.0
        assert extra.usage_characters == 100


class TestBaseResponse:
    """测试基础响应"""
    
    def test_success_response(self):
        """测试成功响应"""
        response = BaseResponse(
            status_code=0,
            status_message=""
        )
        
        assert response.is_success is True
        assert response.error_type == "未知错误"
    
    def test_error_response(self):
        """测试错误响应"""
        response = BaseResponse(
            status_code=1001,
            status_message="超时"
        )
        
        assert response.is_success is False
        assert response.error_type == "超时"


class TestT2AResponse:
    """测试T2A响应模型"""
    
    def test_success_response(self):
        """测试成功响应"""
        data = T2AData(
            audio="48656c6c6f",
            status=2,
            subtitle_file="https://example.com/subtitle.srt"
        )
        
        extra = T2AExtra(
            audio_length=5000,
            audio_sample_rate=32000,
            audio_size=100000,
            audio_bitrate=128000,
            audio_format="mp3",
            audio_channel=1,
            invisible_character_ratio=0.0,
            usage_characters=100
        )
        
        base_resp = BaseResponse(status_code=0, status_message="")
        
        response = T2AResponse(
            data=data,
            extra_info=extra,
            trace_id="test_trace_id",
            base_resp=base_resp
        )
        
        assert response.data == data
        assert response.extra_info == extra
        assert response.trace_id == "test_trace_id"
        assert response.base_resp == base_resp


class TestPronunciationDict:
    """测试发音字典"""
    
    def test_pronunciation_dict(self):
        """测试发音字典"""
        pron_dict = PronunciationDict(tone=["tone1", "tone2"])
        
        assert pron_dict.tone == ["tone1", "tone2"]


class TestTimberWeight:
    """测试音色权重"""
    
    def test_timber_weight(self):
        """测试音色权重"""
        timber = TimberWeight(voice_id="Wise_Woman", weight=50)
        
        assert timber.voice_id == "Wise_Woman"
        assert timber.weight == 50
    
    def test_invalid_weight(self):
        """测试无效权重"""
        with pytest.raises(ValueError):
            TimberWeight(voice_id="Wise_Woman", weight=150)  # 超出范围

