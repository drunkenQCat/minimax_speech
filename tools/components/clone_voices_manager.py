import streamlit as st

from components.voice_manager import VoiceManager


def render_clone_voices_manager(voice_manager: VoiceManager):
    # 搜索音色
    voices = voice_manager.get_voices()
    if not voices:
        st.info("暂无可用音色进行测试")
        return

    st.subheader("克隆音色")
    col_search, col_clear = st.columns([3, 1])

    with col_search:
        search_voice = st.text_input(
            "🔍 搜索音色",
            placeholder="输入音色ID或描述进行搜索...",
            help="支持按音色ID或描述搜索，搜索结果会显示在下拉菜单中",
            key="test_voice_search",
            value=st.session_state.get("test_voice_search", ""),
        )

    with col_clear:
        if not search_voice:
            if st.button("🗑️ 清除", help="清除搜索条件，显示所有音色"):
                # 清除搜索状态
                if "test_voice_search" in st.session_state:
                    del st.session_state.test_voice_search
                st.rerun()

    # 过滤音色
    if search_voice:
        filtered_test_voices = [
            voice
            for voice in voices
            if search_voice.lower() in voice.voice_id.lower()
            or (
                voice.description
                and search_voice.lower() in voice.description[0].lower()
            )
        ]
    else:
        filtered_test_voices = voices

    # 显示搜索状态
    if search_voice:
        if filtered_test_voices:
            st.success(
                f"🔍 搜索 '{search_voice}' 找到 {len(filtered_test_voices)} 个匹配音色"
            )
            voice_manager.current_voice = filtered_test_voices[0].voice_id
        else:
            st.warning(f"🔍 搜索 '{search_voice}' 没有找到匹配的音色")

    # 选择音色
    voice_options = {
        f"{v.voice_id} ({v.description or '未命名'})": v.voice_id
        for v in filtered_test_voices
    }

    if voice_options:
        st.session_state.voice_options = voice_options
        # 根据搜索结果调整下拉菜单的提示
        if search_voice and filtered_test_voices:
            selectbox_label = (
                f"🎯 选择音色 (找到 {len(filtered_test_voices)} 个匹配结果)"
            )
            selectbox_help = (
                f"搜索结果：'{search_voice}' 匹配到 {len(filtered_test_voices)} 个音色"
            )
        elif search_voice and not filtered_test_voices:
            selectbox_label = "❌ 选择音色 (无匹配结果)"
            selectbox_help = f"搜索 '{search_voice}' 没有找到匹配的音色"
        else:
            selectbox_label = "选择音色"
            selectbox_help = "选择要测试的音色"

        # 处理快速测试音色的自动选择
        quick_test_voice_id = st.session_state.get("quick_test_voice")
        default_index = 0

        if quick_test_voice_id:
            # 查找快速测试音色在选项中的索引
            for i, (display_name, voice_id) in enumerate(voice_options.items()):
                if voice_id == quick_test_voice_id:
                    default_index = i
                    break

        def update_selected_voice():
            """更新选中的音色"""
            voice_id = st.session_state.get("selected_clone_voice_num", "")
            __import__("ipdb").set_trace()
            voice_manager.current_voice = (
                st.session_state.voice_options[voice_id] if voice_id else ""
            )

        st.selectbox(
            selectbox_label,
            options=list(voice_options.keys()),
            index=default_index,
            help=selectbox_help,
            on_change=update_selected_voice,
            key="selected_clone_voice_num",
        )
    else:
        st.warning("没有可用的音色进行测试")
