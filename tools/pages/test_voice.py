"""
测试音色页面
"""

import streamlit as st
import os
import json
import tempfile
import time
import re
import hashlib
import binascii

import numpy as np
import pandas as pd
import io
import openpyxl
from pypinyin import pinyin, Style

import os
import tempfile
import streamlit as st
import sys
from pathlib import Path


# 添加components目录到Python路径
components_dir = Path(__file__).parent.parent / "components"
sys.path.insert(0, str(components_dir))

from components.voice_manager import VoiceManager
from components.audio_parameters import render_audio_parameters
from components.clone_voices_manager import render_clone_voices_manager
from components.system_voices_manager import render_system_voices_manager
from utils import generate_safe_filename


def render_test_voice(voice_manager: VoiceManager):
    """渲染测试音色页面"""
    st.header("🎤 测试音色")

    # 处理快速测试跳转
    if st.session_state.get("switch_to_test_tab", False) and st.session_state.get(
        "quick_test_voice"
    ):
        st.success(
            f"🎯 已跳转到测试页面，准备测试音色: {st.session_state.quick_test_voice}"
        )
        # 清除跳转标志，但保留音色ID
        st.session_state.switch_to_test_tab = False

    # 显示快速测试状态和清除按钮
    if st.session_state.get("quick_test_voice"):
        col_status, col_clear = st.columns([3, 1])
        with col_status:
            st.info(f"🎯 快速测试模式：已选择音色 {st.session_state.quick_test_voice}")
        with col_clear:
            if st.button("🗑️ 清除快速测试", help="清除快速测试状态"):
                del st.session_state.quick_test_voice
                st.rerun()

    # 显示当前选择的数据状态
    if "file_prefix" in st.session_state and st.session_state.file_prefix:
        st.info(
            f"📋 当前选择: {st.session_state.file_prefix} | 搜索关键词: {st.session_state.get('test_voice_search', '无')}"
        )

        # 添加清除选择按钮
        if st.button("🗑️ 清除选择", help="清除当前选择的数据"):
            # 清除所有相关状态
            for key in ["test_voice_search", "test_text", "file_prefix"]:
                if key in st.session_state:
                    del st.session_state[key]
            st.rerun()

    operation_col, explain_col = st.columns([3, 1])

    with operation_col:

        st.markdown("### 第一步：选择音色")
        if st.toggle("🔄 切换到MiniMax预设音色", key="switch_to_test_tab", value=False):
            render_system_voices_manager(voice_manager)
        else:
            render_clone_voices_manager(voice_manager)

        st.markdown("### 第二步：输入测试文本")
        st.text_area(
            "测试文本",
            value=st.session_state.get(
                "test_text",
                "你好，这是一个测试音频。Hello, this is a test audio.",
            ),
            height=100,
            help="输入要转换为语音的文本",
            key="test_text",
        )
        st.markdown("### 第三步：调整音频参数")
        render_audio_parameters(voice_manager)

    with explain_col:
        st.info(
            """
        **使用说明：**
        
        1. 使用搜索框快速找到想要的音色
        2. 选择一个已准备好的音色
        3. 输入要测试的文本
        4. 调整音频参数
        5. 点击生成按钮
        6. 播放或下载生成的音频
        
        **搜索功能：**
        - 支持按音色ID搜索
        - 支持按音色描述搜索
        - 不区分大小写
        - 实时过滤显示结果
        
        **音频参数：**
        - 语速: 0.5-2.0，1.0为正常速度
        - 音量: 0-10，1.0为正常音量
        - 音调: -12到12，0为正常音调
        - 情感: 选择语音的情感表达
        - 语言增强: 提高特定语言的发音质量
        
        **支持的音频格式：**
        - MP3 (默认)
        - 采样率: 44100
        - 比特率: 256kbps
        """
        )
