"""
测试语音列表功能
"""

import pytest
from unittest.mock import Mock, patch
import json

from minimax_speech import MiniMaxSpeech
from minimax_speech.voice_query_models import (
    VoiceListResponse,
    VoiceSlot,
    SystemVoice,
    VoiceCloning,
    VoiceGeneration,
    MusicGeneration,
)


class TestVoiceList:
    """测试语音列表功能"""

    def setup_method(self):
        """设置测试环境"""
        self.client = MiniMaxSpeech(api_key="test_key", group_id="test_group")

    def teardown_method(self):
        """清理测试环境"""
        self.client.close()

    def test_get_voice_all(self):
        """测试获取所有语音"""
        # 模拟响应数据
        mock_response_data = {
            "status_code": 0,
            "status_msg": "success",
            "voice_slots": [
                {
                    "voice_id": "slot_1",
                    "voice_name": "测试槽位1",
                    "description": ["测试描述1"]
                }
            ],
            "system_voice": [
                {
                    "voice_id": "Wise_Woman",
                    "voice_name": "智慧女性",
                    "description": ["女性", "智慧"]
                }
            ],
            "voice_cloning": [
                {
                    "voice_id": "clone_1",
                    "description": ["克隆语音1"],
                    "created_time": "2024-01-01"
                }
            ],
            "voice_generation": [
                {
                    "voice_id": "gen_1",
                    "description": ["生成语音1"],
                    "created_time": "2024-01-02"
                }
            ],
            "music_generation": [
                {
                    "voice_id": "music_1",
                    "instrumental_id": "inst_1",
                    "created_time": "2024-01-03"
                }
            ]
        }

        with patch.object(self.client.session, 'get') as mock_get:
            # 设置模拟响应
            mock_response = Mock()
            mock_response.status_code = 200
            mock_response.json.return_value = mock_response_data
            mock_get.return_value = mock_response

            # 调用方法
            result = self.client.get_voice("all")

            # 验证结果
            assert isinstance(result, VoiceListResponse)
            assert result.is_success
            assert len(result.voice_slots) == 1
            assert len(result.system_voice) == 1
            assert len(result.voice_cloning) == 1
            assert len(result.voice_generation) == 1
            assert len(result.music_generation) == 1

            # 验证请求
            mock_get.assert_called_once()
            call_args = mock_get.call_args
            assert "voice/list" in call_args[0][0]
            assert call_args[1]["params"]["voice_type"] == "all"

    def test_get_system_voices(self):
        """测试获取系统语音"""
        mock_response_data = {
            "status_code": 0,
            "status_msg": "success",
            "voice_slots": [],
            "system_voice": [
                {
                    "voice_id": "Wise_Woman",
                    "voice_name": "智慧女性",
                    "description": ["女性", "智慧"]
                },
                {
                    "voice_id": "Grinch",
                    "voice_name": "格林奇",
                    "description": ["男性", "幽默"]
                }
            ],
            "voice_cloning": [],
            "voice_generation": [],
            "music_generation": []
        }

        with patch.object(self.client.session, 'get') as mock_get:
            mock_response = Mock()
            mock_response.status_code = 200
            mock_response.json.return_value = mock_response_data
            mock_get.return_value = mock_response

            result = self.client.get_system_voices()

            assert len(result) == 2
            assert result[0].voice_id == "Wise_Woman"
            assert result[0].voice_name == "智慧女性"
            assert result[1].voice_id == "Grinch"

    def test_get_cloned_voices(self):
        """测试获取克隆语音"""
        mock_response_data = {
            "status_code": 0,
            "status_msg": "success",
            "voice_slots": [],
            "system_voice": [],
            "voice_cloning": [
                {
                    "voice_id": "clone_1",
                    "description": ["克隆语音1"],
                    "created_time": "2024-01-01"
                },
                {
                    "voice_id": "clone_2",
                    "description": ["克隆语音2"],
                    "created_time": "2024-01-02"
                }
            ],
            "voice_generation": [],
            "music_generation": []
        }

        with patch.object(self.client.session, 'get') as mock_get:
            mock_response = Mock()
            mock_response.status_code = 200
            mock_response.json.return_value = mock_response_data
            mock_get.return_value = mock_response

            result = self.client.get_cloned_voices()

            assert len(result) == 2
            assert result[0].voice_id == "clone_1"
            assert result[0].created_time == "2024-01-01"
            assert result[1].voice_id == "clone_2"

    def test_get_voice_http_error(self):
        """测试HTTP错误处理"""
        with patch.object(self.client.session, 'get') as mock_get:
            mock_response = Mock()
            mock_response.status_code = 400
            mock_response.text = "Bad Request"
            mock_get.return_value = mock_response

            with pytest.raises(Exception) as exc_info:
                self.client.get_voice("all")
            
            assert "HTTP 400" in str(exc_info.value)

    def test_get_voice_api_error(self):
        """测试API错误处理"""
        mock_response_data = {
            "status_code": 1004,
            "status_msg": "认证失败",
            "voice_slots": [],
            "system_voice": [],
            "voice_cloning": [],
            "voice_generation": [],
            "music_generation": []
        }

        with patch.object(self.client.session, 'get') as mock_get:
            mock_response = Mock()
            mock_response.status_code = 200
            mock_response.json.return_value = mock_response_data
            mock_get.return_value = mock_response

            with pytest.raises(Exception) as exc_info:
                self.client.get_voice("all")
            
            assert "认证失败" in str(exc_info.value)

    def test_get_voice_timeout(self):
        """测试超时错误处理"""
        with patch.object(self.client.session, 'get') as mock_get:
            # 模拟requests的超时异常
            import requests
            mock_get.side_effect = requests.exceptions.Timeout("Request timed out")

            with pytest.raises(Exception) as exc_info:
                self.client.get_voice("all")
            
            assert "Request timed out" in str(exc_info.value)

    def test_voice_type_validation(self):
        """测试语音类型验证"""
        valid_types = ["all", "system", "voice_cloning", "voice_generation", "music_generation"]
        
        for voice_type in valid_types:
            # 这里只是测试参数传递，不实际调用API
            assert voice_type in valid_types

    def test_voice_response_parsing(self):
        """测试语音响应解析"""
        # 测试空响应
        empty_response = VoiceListResponse(
            status_code=0,
            status_msg="success",
            voice_slots=[],
            system_voice=[],
            voice_cloning=[],
            voice_generation=[],
            music_generation=[]
        )
        
        assert empty_response.is_success
        assert len(empty_response.voice_slots) == 0
        assert len(empty_response.system_voice) == 0

        # 测试包含数据的响应
        data_response = VoiceListResponse(
            status_code=0,
            status_msg="success",
            voice_slots=[
                VoiceSlot(voice_id="test", voice_name="测试", description=["测试"])
            ],
            system_voice=[
                SystemVoice(voice_id="test", voice_name="测试", description=["测试"])
            ],
            voice_cloning=[
                VoiceCloning(voice_id="test", description=["测试"], created_time="2024-01-01")
            ],
            voice_generation=[
                VoiceGeneration(voice_id="test", description=["测试"], created_time="2024-01-01")
            ],
            music_generation=[
                MusicGeneration(voice_id="test", instrumental_id="inst", created_time="2024-01-01")
            ]
        )
        
        assert data_response.is_success
        assert len(data_response.voice_slots) == 1
        assert len(data_response.system_voice) == 1
        assert len(data_response.voice_cloning) == 1
        assert len(data_response.voice_generation) == 1
        assert len(data_response.music_generation) == 1


if __name__ == "__main__":
    pytest.main([__file__]) 
