"""
音色列表页面
"""

import binascii
import os
import sys
import tempfile
from pathlib import Path

import streamlit as st

# 添加components目录到Python路径
components_dir = Path(__file__).parent.parent / "components"
sys.path.insert(0, str(components_dir))

from components.voice_manager import VoiceManager


def render_voice_list(voice_manager: VoiceManager):
    st.header("📋 音色列表")

    voices = voice_manager.get_voices()

    if not voices:
        st.info("暂无克隆音色")
    else:
        # 初始化多选状态
        if "selected_voices" not in st.session_state:
            st.session_state.selected_voices = set()
        if "show_bulk_confirm" not in st.session_state:
            st.session_state.show_bulk_confirm = False

        # 排序功能
        col_sort, col_bulk = st.columns([2, 2])
        with col_sort:
            sort_by = st.selectbox(
                "🔄 排序方式",
                options=[
                    "创建时间 (最新)",
                    "创建时间 (最旧)",
                    "音色ID (A-Z)",
                    "音色ID (Z-A)",
                    "描述 (A-Z)",
                    "描述 (Z-A)",
                ],
                help="选择音色列表的排序方式",
            )
        with col_bulk:
            if st.button("📋 全选/取消全选", help="全选或取消全选所有音色"):
                if len(st.session_state.selected_voices) == len(voices):
                    st.session_state.selected_voices.clear()
                else:
                    st.session_state.selected_voices = {
                        voice.voice_id for voice in voices
                    }
                st.rerun()
            if st.session_state.selected_voices:
                if st.button(
                    f"🗑️ 批量删除选中({len(st.session_state.selected_voices)})",
                    type="primary",
                ):
                    st.session_state.show_bulk_confirm = True

        # 批量删除确认
        if st.session_state.show_bulk_confirm:
            st.warning(
                f"确认要删除选中的 {len(st.session_state.selected_voices)} 个音色吗？"
            )
            col_confirm, col_cancel = st.columns(2)
            with col_confirm:
                if st.button("✅ 确认批量删除", type="primary"):
                    success_count = 0
                    for voice_id in list(st.session_state.selected_voices):
                        if voice_manager.delete_voice(voice_id):
                            success_count += 1
                    st.success(f"成功删除 {success_count} 个音色")
                    st.session_state.selected_voices.clear()
                    st.session_state.show_bulk_confirm = False
                    st.rerun()
            with col_cancel:
                if st.button("❌ 取消"):
                    st.session_state.show_bulk_confirm = False
                    st.rerun()

        # 排序音色列表
        sorted_voices = voices.copy()
        if sort_by == "创建时间 (最新)":
            sorted_voices.sort(key=lambda x: x.created_time, reverse=True)
        elif sort_by == "创建时间 (最旧)":
            sorted_voices.sort(key=lambda x: x.created_time, reverse=False)
        elif sort_by == "音色ID (A-Z)":
            sorted_voices.sort(key=lambda x: x.voice_id, reverse=False)
        elif sort_by == "音色ID (Z-A)":
            sorted_voices.sort(key=lambda x: x.voice_id, reverse=True)
        elif sort_by == "描述 (A-Z)":
            sorted_voices.sort(key=lambda x: (x.description or ""), reverse=False)
        elif sort_by == "描述 (Z-A)":
            sorted_voices.sort(key=lambda x: (x.description or ""), reverse=True)

        st.subheader(f"音色列表 ({len(sorted_voices)} 个)")
        for i, voice in enumerate(sorted_voices):
            with st.container():
                col_check, col1, col2, col3, col4, col5 = st.columns(
                    [0.5, 2, 2, 2, 1, 1]
                )
                with col_check:
                    is_checked = voice.voice_id in st.session_state.selected_voices
                    if st.checkbox(
                        "选择",
                        value=is_checked,
                        key=f"check_{voice.voice_id}",
                        label_visibility="collapsed",
                    ):
                        st.session_state.selected_voices.add(voice.voice_id)
                    else:
                        st.session_state.selected_voices.discard(voice.voice_id)
                with col1:
                    st.write(f"**{voice.voice_id}**")
                with col2:
                    st.write(voice.description or "未命名")
                with col3:
                    st.write(voice.created_time)
                with col4:
                    if st.button("🗑️ 删除", key=f"delete_{voice.voice_id}"):
                        st.session_state.confirm_delete_id = voice.voice_id
                with col5:
                    if st.button(
                        "🎤 测试",
                        key=f"test_{voice.voice_id}",
                        help="快速测试此音色",
                    ):
                        st.session_state.quick_test_voice = voice.voice_id
                        st.session_state.switch_to_test_tab = True
                        st.rerun()
                if st.session_state.confirm_delete_id == voice.voice_id:
                    st.warning(f"确认要删除 {voice.voice_id} 吗？")
                    col_c1, col_c2 = st.columns(2)
                    with col_c1:
                        if st.button("✅ 确认删除", key=f"confirm_{voice.voice_id}"):
                            voice_manager.delete_voice(voice.voice_id)
                            st.session_state.confirm_delete_id = None
                            st.rerun()
                    with col_c2:
                        if st.button("❌ 取消", key=f"cancel_{voice.voice_id}"):
                            st.session_state.confirm_delete_id = None
                st.divider()

