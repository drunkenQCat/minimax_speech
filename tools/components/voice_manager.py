"""
MiniMax 音色管理器核心类
"""

import os
import streamlit as st
from typing import List, Optional
from minimax_speech import MiniMaxSpeech
from minimax_speech.voice_query_models import VoiceCloning
from minimax_speech.tts_models import T2AResponse


class VoiceManager:
    """音色管理器"""

    client: MiniMaxSpeech
    voices_cache: list[VoiceCloning] | None
    voices_cache_time: int
    current_voice: str = ""

    def __init__(self) -> None:
        api_key = os.getenv("MINIMAX_API_KEY", "")
        group_id = os.getenv("MINIMAX_GROUP_ID", "")
        self.voices_cache = []
        self.voices_cache_time = 0
        self.init_client(api_key, group_id)
        # 初始化 session_state 中的确认状态
        if "confirm_delete_id" not in st.session_state:
            st.session_state.confirm_delete_id = None

    def init_client(self, api_key: str, group_id: str):
        """初始化客户端"""
        try:
            self.client = MiniMaxSpeech(api_key=api_key, group_id=group_id)
            return True
        except Exception as e:
            st.error(f"初始化客户端失败: {str(e)}")
            return False

    def get_voices(self, force_refresh: bool = False):
        """获取音色列表"""
        if (
            self.voices_cache is None
            or force_refresh
            or self.voices_cache_time is None
            or (int(st.session_state.get("current_time", 0)) - self.voices_cache_time)
            > 300
        ):  # 5分钟缓存

            try:
                self.voices_cache = self.client.get_cloned_voices()
                self.voices_cache_time = st.session_state.get("current_time", 0)
                return self.voices_cache
            except Exception as e:
                st.error(f"获取音色列表失败: {str(e)}")
                return []
        return self.voices_cache

    def delete_voice(self, voice_id: str):
        """删除音色"""
        try:
            result = self.client.voice_delete(voice_id)
            if result.base_resp.is_success:
                st.success(f"成功删除音色: {voice_id}")
                # 刷新缓存
                self.get_voices(force_refresh=True)
                return True
            else:
                st.error(f"删除音色失败: {result.base_resp.error_type}")
                return False
        except Exception as e:
            st.error(f"删除音色时发生错误: {str(e)}")
            return False

    def clone_voice(self, file_id: int, voice_id: str, **kwargs):
        """克隆音色"""
        try:
            print(file_id)
            print(voice_id)
            print(kwargs)
            result = self.client.voice_clone_simple(
                file_id=file_id, voice_id=voice_id, **kwargs
            )
            if result.base_resp.is_success:
                st.success(f"成功克隆音色: {voice_id}")
                # 刷新缓存
                self.get_voices(force_refresh=True)
                return True
            else:
                st.error(f"克隆音色失败: {result.base_resp.error_type}")
                return False
        except Exception as e:
            st.error(f"克隆音色时发生错误: {str(e)}")
            return False

    def test_voice(self, voice_id: str, text: str, **kwargs) -> T2AResponse | None:
        """测试音色"""
        try:
            result = self.client.text_to_speech_simple(
                text=text, voice_id=voice_id, **kwargs
            )
            if result.base_resp.is_success:
                return result
            else:
                st.error(f"生成测试音频失败: {result.base_resp.error_type}")
                return None
        except Exception as e:
            st.error(f"生成测试音频时发生错误: {str(e)}")
            return None

