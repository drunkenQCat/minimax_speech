"""
MiniMax 音色管理器主应用
"""

import streamlit as st
import os
import json
import sys
from pathlib import Path


# 添加当前目录到Python路径
current_dir = Path(__file__).parent
sys.path.insert(0, str(current_dir))

from components import VoiceManager, render_sidebar
from components.excel_manager import render_excel_manager
from pages import (
    render_voice_list,
    render_test_voice,
    render_add_voice,
    render_batch_upload,
)


def main():
    """主应用函数"""
    st.set_page_config(
        page_title="MiniMax 音色管理器",
        page_icon="🎵",
        layout="wide",
        initial_sidebar_state="collapsed",
    )

    st.title("🎵 MiniMax 音色管理器")
    st.markdown("---")

    # 初始化管理器
    if "voice_manager" not in st.session_state:
        st.session_state.voice_manager = VoiceManager()

    voice_manager = st.session_state.voice_manager

    # 渲染侧边栏
    render_sidebar(voice_manager)

    # 主界面
    if not voice_manager.client:
        st.info("请在侧边栏配置 API Key 和 Group ID 并连接")
        return
    with st.expander("📊 剧本数据", expanded=False):
        # st.markdown("正在开发中...")
        st.markdown("这里可以查看和管理剧本数据，包括音色列表、批量上传等功能。")
        render_excel_manager()

    if st.button("🔄 刷新音色列表"):
        if voice_manager.client:
            voice_manager.get_voices(force_refresh=True)
            st.success("音色列表已刷新！")
        else:
            st.error("请先连接客户端")

    # 创建标签页
    tab1, tab3 = st.tabs(["🎤 测试音色", "➕ 添加音色"])
    # 标签页1: 测试音色
    with tab1:
        render_test_voice(voice_manager)

    # with tab2:
    #     render_voice_list(voice_manager)
    # 标签页3: 添加音色
    with tab3:
        # st.markdown("正在开发中...")
        render_add_voice(voice_manager)


if __name__ == "__main__":
    config_path = os.path.join(os.path.dirname(__file__), "config.json")
    if os.path.exists(config_path):
        with open(config_path, "r", encoding="utf-8") as f:
            config_data = json.load(f)
        for key, value in config_data.items():
            # 将所有配置项加入系统环境变量
            os.environ[str(key)] = str(value)

    main()
