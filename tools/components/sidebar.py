"""
侧边栏组件
"""

import os
import streamlit as st
import sys
from pathlib import Path

# 添加当前目录到Python路径
current_dir = Path(__file__).parent
sys.path.insert(0, str(current_dir))

from voice_manager import VoiceManager


def render_sidebar(voice_manager: VoiceManager):
    """渲染侧边栏"""
    with st.sidebar:
        st.header("🔧 配置")

        api_key = st.text_input(
            "API Key",
            type="password",
            help="输入你的 MiniMax API Key",
            value=os.environ.get("MINIMAX_API_KEY", ""),
        )

        group_id = st.text_input(
            "Group ID",
            help="输入你的 Group ID",
            value=os.environ.get("MINIMAX_GROUP_ID", ""),
        )
        voice_manager.init_client(api_key, group_id)
        voice_manager.get_voices(force_refresh=True)

        if st.button("🔗 连接", type="primary"):
            if api_key and group_id:
                if voice_manager.init_client(api_key, group_id):
                    st.success("连接成功！")
                    st.session_state.connected = True
            else:
                st.error("请填写 API Key 和 Group ID")

        st.markdown("---")

