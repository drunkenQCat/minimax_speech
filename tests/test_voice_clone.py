"""
测试语音克隆功能
"""

import pytest
from unittest.mock import Mock, patch
import json

from minimax_speech import MiniMaxSpeech
from minimax_speech.voice_clone_models import VoiceCloneRequest, VoiceCloneResponse


class TestVoiceClone:
    """测试语音克隆功能"""

    def setup_method(self):
        """设置测试环境"""
        self.client = MiniMaxSpeech(api_key="test_key", group_id="test_group")

    def teardown_method(self):
        """清理测试环境"""
        self.client.close()

    def test_voice_clone_success(self):
        """测试语音克隆成功"""
        # 模拟响应数据
        mock_response_data = {
            "input_sensitive": False,
            "base_resp": {
                "status_code": 0,
                "status_msg": "success"
            }
        }

        with patch.object(self.client.session, 'post') as mock_post:
            # 设置模拟响应
            mock_response = Mock()
            mock_response.status_code = 200
            mock_response.json.return_value = mock_response_data
            mock_post.return_value = mock_response

            # 创建请求
            request = VoiceCloneRequest(
                file_id="test_file_id",
                voice_id="TestVoice001",
                need_noise_reduction=True,
                text="测试文本",
                model="speech-02-hd",
                accuracy=0.8,
                need_volume_normalization=True
            )

            # 调用方法
            result = self.client.voice_clone(request)

            # 验证结果
            assert isinstance(result, VoiceCloneResponse)
            assert result.input_sensitive is False
            assert result.base_resp.is_success

            # 验证请求
            mock_post.assert_called_once()
            call_args = mock_post.call_args
            assert "voice_clone" in call_args[0][0]
            assert call_args[1]["json"]["file_id"] == "test_file_id"
            assert call_args[1]["json"]["voice_id"] == "TestVoice001"

    def test_voice_clone_simple(self):
        """测试简化语音克隆接口"""
        mock_response_data = {
            "input_sensitive": True,
            "base_resp": {
                "status_code": 0,
                "status_msg": "success"
            }
        }

        with patch.object(self.client.session, 'post') as mock_post:
            mock_response = Mock()
            mock_response.status_code = 200
            mock_response.json.return_value = mock_response_data
            mock_post.return_value = mock_response

            result = self.client.voice_clone_simple(
                file_id="test_file_id",
                voice_id="SimpleVoice001",
                need_noise_reduction=False,
                text="简化接口测试",
                model="speech-01-turbo",
                accuracy=0.7,
                need_volume_normalization=False
            )

            assert isinstance(result, VoiceCloneResponse)
            assert result.input_sensitive is True
            assert result.base_resp.is_success

    def test_voice_clone_validation_voice_id_too_short(self):
        """测试voice_id太短的验证"""
        request = VoiceCloneRequest(
            file_id="test_file_id",
            voice_id="123",  # 太短
            text="测试"
        )

        with pytest.raises(ValueError) as exc_info:
            self.client.voice_clone(request)
        
        assert "at least 8 characters" in str(exc_info.value)

    def test_voice_clone_validation_voice_id_no_letter_start(self):
        """测试voice_id不以字母开头的验证"""
        request = VoiceCloneRequest(
            file_id="test_file_id",
            voice_id="12345678",  # 不以字母开头
            text="测试"
        )

        with pytest.raises(ValueError) as exc_info:
            self.client.voice_clone(request)
        
        assert "start with a letter" in str(exc_info.value)

    def test_voice_clone_validation_voice_id_no_digit(self):
        """测试voice_id没有数字的验证"""
        request = VoiceCloneRequest(
            file_id="test_file_id",
            voice_id="abcdefgh",  # 只有字母，没有数字
            text="测试"
        )

        with pytest.raises(ValueError) as exc_info:
            self.client.voice_clone(request)
        
        assert "both letters and numbers" in str(exc_info.value)

    def test_voice_clone_validation_text_too_long(self):
        """测试text过长的验证"""
        long_text = "a" * 2500  # 超过2000字符
        request = VoiceCloneRequest(
            file_id="test_file_id",
            voice_id="ValidVoice001",
            text=long_text
        )

        with pytest.raises(ValueError) as exc_info:
            self.client.voice_clone(request)
        
        assert "maximum 2000 characters" in str(exc_info.value)

    def test_voice_clone_validation_accuracy_invalid(self):
        """测试accuracy无效的验证"""
        request = VoiceCloneRequest(
            file_id="test_file_id",
            voice_id="ValidVoice001",
            accuracy=1.5  # 超出范围[0,1]
        )

        with pytest.raises(ValueError) as exc_info:
            self.client.voice_clone(request)
        
        assert "between 0 and 1" in str(exc_info.value)

    def test_voice_clone_validation_invalid_model(self):
        """测试无效model的验证"""
        request = VoiceCloneRequest(
            file_id="test_file_id",
            voice_id="ValidVoice001",
            model="invalid-model"
        )

        with pytest.raises(ValueError) as exc_info:
            self.client.voice_clone(request)
        
        assert "Invalid model" in str(exc_info.value)

    def test_voice_clone_http_error(self):
        """测试HTTP错误处理"""
        with patch.object(self.client.session, 'post') as mock_post:
            mock_response = Mock()
            mock_response.status_code = 400
            mock_response.text = "Bad Request"
            mock_post.return_value = mock_response

            request = VoiceCloneRequest(
                file_id="test_file_id",
                voice_id="ValidVoice001"
            )

            with pytest.raises(Exception) as exc_info:
                self.client.voice_clone(request)
            
            assert "HTTP 400" in str(exc_info.value)

    def test_voice_clone_api_error(self):
        """测试API错误处理"""
        mock_response_data = {
            "input_sensitive": False,
            "base_resp": {
                "status_code": 1004,
                "status_msg": "认证失败"
            }
        }

        with patch.object(self.client.session, 'post') as mock_post:
            mock_response = Mock()
            mock_response.status_code = 200
            mock_response.json.return_value = mock_response_data
            mock_post.return_value = mock_response

            request = VoiceCloneRequest(
                file_id="test_file_id",
                voice_id="ValidVoice001"
            )

            with pytest.raises(Exception) as exc_info:
                self.client.voice_clone(request)
            
            assert "认证失败" in str(exc_info.value)

    def test_voice_clone_timeout(self):
        """测试超时错误处理"""
        with patch.object(self.client.session, 'post') as mock_post:
            import requests
            mock_post.side_effect = requests.exceptions.Timeout("Request timed out")

            request = VoiceCloneRequest(
                file_id="test_file_id",
                voice_id="ValidVoice001"
            )

            with pytest.raises(Exception) as exc_info:
                self.client.voice_clone(request)
            
            assert "Request timed out" in str(exc_info.value)

    def test_voice_clone_request_parsing(self):
        """测试请求解析"""
        # 测试完整的请求对象
        request = VoiceCloneRequest(
            file_id="test_file_id",
            voice_id="TestVoice001",
            need_noise_reduction=True,
            text="测试文本",
            model="speech-02-hd",
            accuracy=0.8,
            need_volume_normalization=True
        )
        
        assert request.file_id == "test_file_id"
        assert request.voice_id == "TestVoice001"
        assert request.need_noise_reduction is True
        assert request.text == "测试文本"
        assert request.model == "speech-02-hd"
        assert request.accuracy == 0.8
        assert request.need_volume_normalization is True

    def test_voice_clone_response_parsing(self):
        """测试响应解析"""
        # 测试完整的响应对象
        response = VoiceCloneResponse(
            input_sensitive=True,
            base_resp={
                "status_code": 0,
                "status_msg": "success"
            }
        )
        
        assert response.input_sensitive is True
        assert response.base_resp.is_success
        assert response.base_resp.status_code == 0
        assert response.base_resp.status_msg == "success"

    def test_voice_clone_valid_models(self):
        """测试有效的模型"""
        valid_models = ["speech-02-hd", "speech-02-turbo", "speech-01-hd", "speech-01-turbo"]
        
        for model in valid_models:
            request = VoiceCloneRequest(
                file_id="test_file_id",
                voice_id="ValidVoice001",
                model=model
            )
            # 这里只是测试参数传递，不实际调用API
            assert request.model == model

    def test_voice_clone_optional_parameters(self):
        """测试可选参数"""
        # 测试最小参数
        request = VoiceCloneRequest(
            file_id="test_file_id",
            voice_id="ValidVoice001"
        )
        
        assert request.file_id == "test_file_id"
        assert request.voice_id == "ValidVoice001"
        assert request.need_noise_reduction is False
        assert request.text is None
        assert request.model is None
        assert request.accuracy == 0.7
        assert request.need_volume_normalization is False


if __name__ == "__main__":
    pytest.main([__file__]) 