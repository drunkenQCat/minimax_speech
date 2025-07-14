"""
MiniMax 音色管理工具
基于 Streamlit 的 Web 界面，用于管理 MiniMax 音色
"""

import streamlit as st
import os
import json
import tempfile
import binascii

import numpy as np
import pandas as pd
import io

# from pathlib import Path
# import sys
from minimax_speech import MiniMaxSpeech
from minimax_speech.tts_models import T2AResponse, Voice
from minimax_speech.voice_query_models import VoiceCloning


# 添加项目根目录到 Python 路径
# project_root = Path(__file__).parent.parent
# sys.path.insert(0, str(project_root))


class VoiceManager:
    """音色管理器"""

    client: MiniMaxSpeech
    voices_cache: list[VoiceCloning] | None
    voices_cache_time: int

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


def main():
    st.set_page_config(
        page_title="MiniMax 音色管理器",
        page_icon="🎵",
        layout="wide",
        initial_sidebar_state="expanded",
    )

    st.title("🎵 MiniMax 音色管理器")
    st.markdown("---")

    # 初始化管理器
    if "voice_manager" not in st.session_state:
        st.session_state.voice_manager = VoiceManager()

    voice_manager = st.session_state.voice_manager

    # 侧边栏配置
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

        if st.button("🔗 连接", type="primary"):
            if api_key and group_id:
                if voice_manager.init_client(api_key, group_id):
                    st.success("连接成功！")
                    st.session_state.connected = True
            else:
                st.error("请填写 API Key 和 Group ID")

        st.markdown("---")

        if st.button("🔄 刷新音色列表"):
            if voice_manager.client:
                voice_manager.get_voices(force_refresh=True)
                st.success("音色列表已刷新！")
            else:
                st.error("请先连接客户端")

    # 主界面
    if not voice_manager.client:
        st.info("请在侧边栏配置 API Key 和 Group ID 并连接")
        return

    # 创建标签页
    tab1, tab2, tab3, tab4, tab5 = st.tabs(
        ["📋 音色列表", "🎤 测试音色", "🎭 系统音色", "➕ 添加音色", "📁 批量上传"]
    )

    # 标签页1: 音色列表
    with tab1:
        st.header("📋 音色列表")

        voices = voice_manager.get_voices()

        if not voices:
            st.info("暂无克隆音色")
        else:
            # 创建数据表格
            voice_data = []
            for voice in voices:
                voice_data.append(
                    {
                        "音色ID": voice.voice_id,
                        "创建时间": voice.created_time,
                        "操作": f"删除_{voice.voice_id}",  # 用于按钮标识
                    }
                )

            # 显示音色列表
            for i, voice in enumerate(voices):
                with st.container():
                    col1, col2, col3, col4, col5 = st.columns([2, 2, 2, 1, 1])

                    with col1:
                        st.write(f"**{voice.voice_id}**")

                    with col2:
                        st.write(voice.description or "未命名")

                    with col3:
                        st.write(voice.created_time)

                    with col4:
                        if st.button("🗑️ 删除", key=f"delete_{voice.voice_id}"):
                            st.session_state.confirm_delete_id = voice.voice_id

                            # if st.button(
                            #     f"确认删除 {voice.voice_id}?",
                            #     key=f"confirm_delete_{voice.voice_id}",
                            # ):
                            #     voice_manager.delete_voice(voice.voice_id)
                            #     st.rerun()

                    if st.session_state.confirm_delete_id == voice.voice_id:
                        st.warning(f"确认要删除 {voice.voice_id} 吗？")
                        col1, col2 = st.columns(2)

                        with col1:
                            if st.button(
                                "✅ 确认删除", key=f"confirm_{voice.voice_id}"
                            ):
                                voice_manager.delete_voice(voice.voice_id)
                                st.session_state.confirm_delete_id = None  # 重置状态
                                st.rerun()

                        with col2:
                            if st.button("❌ 取消", key=f"cancel_{voice.voice_id}"):
                                st.session_state.confirm_delete_id = None
                    st.divider()

    # 标签页2: 测试音色
    with tab2:
        st.header("🎤 测试音色")

        voices = voice_manager.get_voices()

        if not voices:
            st.info("暂无可用音色进行测试")
        else:
            col1, col2 = st.columns(2)

            with col1:
                # 选择音色
                voice_options = {
                    f"{v.voice_id} ({v.description or '未命名'})": v.voice_id
                    for v in voices
                }

                if voice_options:
                    selected_voice = st.selectbox(
                        "选择音色",
                        options=list(voice_options.keys()),
                        help="选择要测试的音色",
                    )

                    # 测试文本
                    test_text = st.text_area(
                        "测试文本",
                        value="你好，这是一个测试音频。Hello, this is a test audio.",
                        height=100,
                        help="输入要转换为语音的文本",
                    )

                    # 音频参数
                    st.subheader("音频参数")

                    col_a, col_b = st.columns(2)
                    with col_a:
                        speed = st.slider("语速", 0.5, 2.0, 1.0, 0.1)
                        volume = st.slider("音量", 0.0, 10.0, 1.0, 0.1)

                    with col_b:
                        pitch = st.slider("音调", -12, 12, 0, 1)
                        model = st.selectbox(
                            "模型", ["speech-02-hd", "speech-01-turbo", "speech-01-hd"]
                        )

                    # 情感参数
                    emotion = st.selectbox(
                        "情感",
                        options=[
                            "无",
                            "happy",
                            "sad",
                            "angry",
                            "fearful",
                            "disgusted",
                            "surprised",
                            "neutral",
                        ],
                        help="选择语音的情感表达",
                    )

                    # 将"无"转换为None
                    emotion_value = None if emotion == "无" else emotion

                    if st.button("🎵 生成测试音频", type="primary"):
                        if test_text.strip():
                            with st.spinner("正在生成音频..."):
                                result = voice_manager.test_voice(
                                    voice_id=voice_options[selected_voice],
                                    text=test_text,
                                    speed=speed,
                                    volume=volume,
                                    pitch=pitch,
                                    emotion=emotion_value,
                                    model=model,
                                    sample_rate=44100,
                                    bitrate=256000,
                                )

                                if result:
                                    # 保存音频文件
                                    audio_data = result.data.audio
                                    audio_data = binascii.unhexlify(audio_data)
                                    if audio_data:
                                        # 创建临时文件
                                        with tempfile.NamedTemporaryFile(
                                            delete=False, suffix=".mp3", mode="wb"
                                        ) as tmp_file:
                                            tmp_file.write(audio_data)
                                            tmp_path = tmp_file.name

                                        # 显示音频播放器
                                        st.audio(tmp_path, format="audio/mp3")

                                        # 提供下载链接
                                        with open(tmp_path, "rb") as f:
                                            st.download_button(
                                                label="📥 下载音频",
                                                data=f.read(),
                                                file_name=f"test_audio_{voice_options[selected_voice]}.mp3",
                                                mime="audio/mp3",
                                            )

                                        # 清理临时文件
                                        os.unlink(tmp_path)
                        else:
                            st.warning("请输入测试文本")
                else:
                    st.warning("没有可用的音色进行测试")

            with col2:
                st.info(
                    """
                **使用说明：**
                
                1. 选择一个已准备好的音色
                2. 输入要测试的文本
                3. 调整音频参数
                4. 点击生成按钮
                5. 播放或下载生成的音频
                
                **支持的音频格式：**
                - MP3 (默认)
                - 采样率: 44100
                - 比特率: 256kbps
                """
                )

    # 标签页3: 系统音色测试
    with tab3:
        st.header("🎭 系统音色测试")

        # 初始化session_state中的系统音色
        if "system_voices" not in st.session_state:
            st.session_state.system_voices = list(Voice)
            st.session_state.api_system_voices = []

        # 获取基础系统音色（枚举中的）
        base_system_voices = list(Voice)
        
        # 合并基础音色和API获取的音色
        system_voices = base_system_voices + st.session_state.api_system_voices
        
        # 添加获取API系统音色的按钮
        col_refresh, col_clear, col_search, col_clear_search = st.columns([1, 1, 2, 1])
        
        with col_refresh:
            if st.button("🔄 获取最新系统音色", help="从API获取最新的系统音色列表"):
                if voice_manager.client:
                    with st.spinner("正在获取系统音色..."):
                        try:
                            # 获取API中的系统音色
                            api_response = voice_manager.client.get_voice("system")
                            if api_response and api_response.system_voice:
                                # 创建API音色对象
                                api_voices = []
                                for voice_info in api_response.system_voice:
                                    # 创建一个类似Voice枚举的对象
                                    class APIVoice:
                                        def __init__(self, voice_id, name, description=""):
                                            self.value = voice_id
                                            self.name = name
                                            self.description = description
                                    
                                    api_voice = APIVoice(
                                        voice_id=voice_info.voice_id,
                                        name=voice_info.voice_name or voice_info.voice_id,
                                        description=voice_info.description or ""
                                    )
                                    api_voices.append(api_voice)
                                
                                # 更新session_state
                                st.session_state.api_system_voices = api_voices
                                st.success(f"成功获取 {len(api_voices)} 个系统音色")
                                st.rerun()
                            else:
                                st.warning("未获取到系统音色")
                        except Exception as e:
                            st.error(f"获取系统音色失败: {str(e)}")
                else:
                    st.error("请先连接客户端")
        
        with col_clear:
            if st.button("🗑️ 清除API音色", help="清除从API获取的音色，只保留基础音色"):
                st.session_state.api_system_voices = []
                st.success("已清除API音色")
                st.rerun()
        
        with col_search:
            # 搜索框
            search_term = st.text_input(
                "🔍 搜索音色",
                placeholder="输入音色名称或描述进行搜索...",
                help="支持按音色ID、名称或描述搜索，搜索结果会显示在下拉菜单中",
                key="search_term"
            )
        
        with col_clear_search:
            if search_term:
                if st.button("🗑️ 清除搜索", help="清除搜索条件，显示所有音色"):
                    # 清除搜索状态
                    if "search_term" in st.session_state:
                        del st.session_state.search_term
                    st.rerun()
            
        # 过滤音色
        if search_term:
            filtered_voices = [
                voice for voice in system_voices
                if search_term.lower() in voice.value.lower() or 
                   search_term.lower() in voice.name.lower() or
                   (hasattr(voice, 'description') and voice.description and 
                    search_term.lower() in voice.description.lower())
            ]
        else:
            filtered_voices = system_voices
        
        # 显示当前音色来源和搜索状态
        if search_term:
            if filtered_voices:
                st.success(f"🔍 搜索 '{search_term}' 找到 {len(filtered_voices)} 个匹配音色 ↓ 请在下拉菜单中选择")
            else:
                st.warning(f"🔍 搜索 '{search_term}' 没有找到匹配的音色")
        else:
            if st.session_state.api_system_voices:
                st.info(f"📊 当前显示 {len(system_voices)} 个音色（基础 {len(base_system_voices)} + API {len(st.session_state.api_system_voices)}）")
            else:
                st.info(f"📊 当前显示 {len(system_voices)} 个基础音色")
        
        if not filtered_voices:
            st.info("没有找到匹配的音色")
        else:
            col1, col2 = st.columns(2)
            
            with col1:
                # 选择音色
                voice_options = {}
                for voice in filtered_voices:
                    if hasattr(voice, 'description') and voice.description:
                        display_name = f"{voice.value} ({voice.name}) - {voice.description}"
                    else:
                        display_name = f"{voice.value} ({voice.name})"
                    voice_options[display_name] = voice.value
                
                # 根据搜索结果调整下拉菜单的提示
                if search_term and filtered_voices:
                    selectbox_label = f"🎯 选择系统音色 (找到 {len(filtered_voices)} 个匹配结果)"
                    selectbox_help = f"搜索结果：'{search_term}' 匹配到 {len(filtered_voices)} 个音色"
                elif search_term and not filtered_voices:
                    selectbox_label = "❌ 选择系统音色 (无匹配结果)"
                    selectbox_help = f"搜索 '{search_term}' 没有找到匹配的音色"
                else:
                    selectbox_label = "选择系统音色"
                    selectbox_help = "选择要测试的系统音色"
                
                selected_voice = st.selectbox(
                    selectbox_label,
                    options=list(voice_options.keys()),
                    help=selectbox_help,
                )
                
                # 测试文本
                test_text = st.text_area(
                    "测试文本",
                    value="你好，这是一个系统音色测试音频。Hello, this is a system voice test.",
                    height=100,
                    help="输入要转换为语音的文本",
                )
                
                # 音频参数
                st.subheader("音频参数")
                
                col_a, col_b = st.columns(2)
                with col_a:
                    speed = st.slider("语速", 0.5, 2.0, 1.0, 0.1, key="sys_speed")
                    volume = st.slider("音量", 0.0, 10.0, 1.0, 0.1, key="sys_volume")
                
                with col_b:
                    pitch = st.slider("音调", -12, 12, 0, 1, key="sys_pitch")
                    model = st.selectbox(
                        "模型", 
                        ["speech-02-hd", "speech-01-turbo", "speech-01-hd"],
                        key="sys_model"
                    )
                
                # 情感参数
                emotion = st.selectbox(
                    "情感",
                    options=[
                        "无",
                        "happy",
                        "sad",
                        "angry",
                        "fearful",
                        "disgusted",
                        "surprised",
                        "neutral",
                    ],
                    help="选择语音的情感表达",
                    key="sys_emotion"
                )
                
                # 将"无"转换为None
                emotion_value = None if emotion == "无" else emotion
                
                if st.button("🎵 生成测试音频", type="primary", key="sys_generate"):
                    if test_text.strip():
                        with st.spinner("正在生成音频..."):
                            result = voice_manager.test_voice(
                                voice_id=voice_options[selected_voice],
                                text=test_text,
                                speed=speed,
                                volume=volume,
                                pitch=pitch,
                                emotion=emotion_value,
                                model=model,
                                sample_rate=44100,
                                bitrate=256000,
                            )
                            
                            if result:
                                # 保存音频文件
                                audio_data = result.data.audio
                                audio_data = binascii.unhexlify(audio_data)
                                if audio_data:
                                    # 创建临时文件
                                    with tempfile.NamedTemporaryFile(
                                        delete=False, suffix=".mp3", mode="wb"
                                    ) as tmp_file:
                                        tmp_file.write(audio_data)
                                        tmp_path = tmp_file.name
                                    
                                    # 显示音频播放器
                                    st.audio(tmp_path, format="audio/mp3")
                                    
                                    # 提供下载链接
                                    with open(tmp_path, "rb") as f:
                                        st.download_button(
                                            label="📥 下载音频",
                                            data=f.read(),
                                            file_name=f"system_voice_{voice_options[selected_voice]}.mp3",
                                            mime="audio/mp3",
                                        )
                                    
                                    # 清理临时文件
                                    os.unlink(tmp_path)
                    else:
                        st.warning("请输入测试文本")
            
            with col2:
                st.info(
                    f"""
                **系统音色说明：**
                
                系统音色是MiniMax提供的预设音色，无需克隆即可直接使用。
                
                **当前音色数量：**
                - 基础音色：{len(base_system_voices)} 个
                - API获取：{len(st.session_state.api_system_voices)} 个
                - 总计：{len(system_voices)} 个
                
                **基础音色：**
                - 智慧女性 (Wise_Woman)
                - 友好人士 (Friendly_Person)
                - 励志女孩 (Inspirational_girl)
                - 深沉男声 (Deep_Voice_Man)
                - 平静女性 (Calm_Woman)
                - 随性男士 (Casual_Guy)
                - 活泼女孩 (Lively_Girl)
                - 耐心男士 (Patient_Man)
                - 年轻骑士 (Young_Knight)
                - 坚定男士 (Determined_Man)
                - 可爱女孩 (Lovely_Girl)
                - 体面男孩 (Decent_Boy)
                - 威严仪态 (Imposing_Manner)
                - 优雅男士 (Elegant_Man)
                - 女修道院长 (Abbess)
                - 甜美女孩2 (Sweet_Girl_2)
                - 热情女孩 (Exuberant_Girl)
                
                **搜索功能：**
                - 支持按音色ID搜索
                - 支持按音色描述搜索
                - 不区分大小写
                """
                )
                
                # 显示所有系统音色列表
                st.subheader("📋 所有系统音色")
                voice_list = []
                for voice in system_voices:
                    description = ""
                    if hasattr(voice, 'description') and voice.description:
                        description = voice.description
                    elif hasattr(voice, 'name'):
                        description = voice.name
                    
                    voice_list.append({
                        "音色ID": voice.value,
                        "描述": description,
                        "来源": "API" if voice in st.session_state.api_system_voices else "基础"
                    })
                
                # 创建可滚动的音色列表
                voice_df = pd.DataFrame(voice_list)
                st.dataframe(
                    voice_df,
                    use_container_width=True,
                    hide_index=True
                )

    # 标签页4: 添加音色
    with tab4:
        st.header("➕ 添加音色")

        col1, col2 = st.columns(2)

        with col1:
            # 文件上传
            uploaded_file = st.file_uploader(
                "选择音频文件",
                type=["wav", "mp3", "m4a", "flac"],
                help="支持 WAV, MP3, M4A, FLAC 格式",
            )

            if uploaded_file:
                st.success(f"已选择文件: {uploaded_file.name}")

                # 显示文件信息
                file_size = uploaded_file.size / 1024 / 1024  # MB
                st.write(f"文件大小: {file_size:.2f} MB")

                # 音色配置
                st.subheader("音色配置")

                voice_id = st.text_input(
                    "音色ID", help="自定义音色ID，必须包含字母和数字，至少8位"
                )

                # 高级选项
                with st.expander("高级选项"):
                    need_noise_reduction = st.checkbox("降噪", value=False)
                    need_volume_normalization = st.checkbox("音量标准化", value=False)
                    accuracy = st.slider("文本验证精度", 0.0, 1.0, 0.7, 0.1)
                    model = st.selectbox(
                        "模型",
                        [
                            "speech-02-hd",
                            "speech-02-turbo",
                            "speech-01-hd",
                            "speech-01-turbo",
                        ],
                    )
                    preview_text = st.text_area("预览文本", help="用于验证音色的文本")

                if st.button("🚀 开始克隆", type="primary"):
                    if voice_id and uploaded_file:
                        # 验证voice_id格式
                        if len(voice_id) < 8:
                            st.error("音色ID必须至少8位")
                        elif not voice_id[0].isalpha():
                            st.error("音色ID必须以字母开头")
                        elif not (
                            any(c.isalpha() for c in voice_id)
                            and any(c.isdigit() for c in voice_id)
                        ):
                            st.error("音色ID必须包含字母和数字")
                        else:
                            with st.spinner("正在上传文件..."):
                                try:
                                    # 保存上传的文件到临时位置
                                    with tempfile.NamedTemporaryFile(
                                        delete=False,
                                        suffix=f".{uploaded_file.name.split('.')[-1]}",
                                    ) as tmp_file:
                                        tmp_file.write(uploaded_file.getvalue())
                                        tmp_path = tmp_file.name

                                    # 上传文件
                                    file_id = voice_manager.client.file_upload(tmp_path)
                                    st.success(f"文件上传成功，ID: {file_id}")

                                    # 开始克隆
                                    with st.spinner("正在克隆音色..."):
                                        success = voice_manager.clone_voice(
                                            file_id=file_id,
                                            voice_id=voice_id,
                                            need_noise_reduction=need_noise_reduction,
                                            need_volume_normalization=need_volume_normalization,
                                            accuracy=accuracy,
                                            model=model,
                                            text=preview_text if preview_text else None,
                                        )

                                        if success:
                                            st.success("音色克隆任务已提交！")
                                            st.info(
                                                "克隆过程可能需要几分钟时间，请稍后刷新音色列表查看状态。"
                                            )

                                    # 清理临时文件
                                    os.unlink(tmp_path)

                                except Exception as e:
                                    st.error(f"处理过程中发生错误: {str(e)}")
                    else:
                        st.warning("请填写音色ID并选择文件")

        with col2:
            st.info(
                """
            **音色克隆说明：**
            
            **支持的音频格式：**
            - WAV, MP3, M4A, FLAC
            
            **音色ID要求：**
            - 至少8位字符
            - 必须以字母开头
            - 必须包含字母和数字
            
            **克隆过程：**
            1. 上传音频文件
            2. 配置音色参数
            3. 提交克隆任务
            4. 等待处理完成
            
            **处理时间：**
            - 通常需要1-5分钟
            - 可以在音色列表中查看状态
            """
            )

    # 标签页5: 批量上传
    with tab5:
        st.header("📁 批量上传")

        # 文件上传
        uploaded_files = st.file_uploader(
            "选择多个音频文件",
            type=["wav", "mp3", "m4a", "flac"],
            accept_multiple_files=True,
            help="可以同时选择多个音频文件进行批量处理",
        )

        if uploaded_files:
            st.success(f"已选择 {len(uploaded_files)} 个文件")

            # 显示文件列表
            st.subheader("文件列表")

            # 创建文件信息表格
            file_info = []
            for i, file in enumerate(uploaded_files):
                file_info.append(
                    {
                        "序号": i + 1,
                        "文件名": file.name,
                        "大小(MB)": f"{file.size / 1024 / 1024:.2f}",
                        "格式": file.name.split(".")[-1].upper(),
                    }
                )

            # 显示文件表格
            for info in file_info:
                col1, col2, col3, col4 = st.columns([1, 3, 1, 1])
                with col1:
                    st.write(info["序号"])
                with col2:
                    st.write(info["文件名"])
                with col3:
                    st.write(info["大小(MB)"])
                with col4:
                    st.write(info["格式"])

            st.divider()

            # 批量配置
            st.subheader("批量配置")

            col1, col2 = st.columns(2)

            with col1:
                # 基础配置
                base_voice_id = st.text_input(
                    "基础音色ID", help="将作为音色ID的前缀，会自动添加序号"
                )

                need_noise_reduction = st.checkbox("降噪", value=False)
                need_volume_normalization = st.checkbox("音量标准化", value=False)
                accuracy = st.slider("文本验证精度", 0.0, 1.0, 0.7, 0.1)
                model = st.selectbox(
                    "模型",
                    [
                        "speech-02-hd",
                        "speech-02-turbo",
                        "speech-01-hd",
                        "speech-01-turbo",
                    ],
                )

            with col2:
                # 自定义音色ID和预览文本
                st.write("自定义音色ID和预览文本:")
                custom_voice_ids = {}
                custom_preview_texts = {}

                # CSV导入功能
                csv_file = st.file_uploader(
                    "从CSV导入配置",
                    type=["csv"],
                    help="CSV文件应包含：文件名,音色ID,预览文本 三列",
                )

                if csv_file:
                    try:
                        # 读取CSV文件
                        csv_content = csv_file.read().decode("utf-8")
                        df = pd.read_csv(
                            io.StringIO(csv_content),
                            na_values=["", "nan", "NaN"],
                            keep_default_na=False,
                        )

                        # 验证CSV格式
                        if len(df.columns) >= 2:
                            # 创建文件名到配置的映射
                            csv_config = {}
                            for _, row in df.iterrows():
                                filename = row.iloc[0]  # 第一列：文件名
                                voice_id = (
                                    row.iloc[1] if len(df.columns) > 1 else None
                                )  # 第二列：音色ID
                                preview_text = (
                                    row.iloc[2] if len(df.columns) > 2 else None
                                )  # 第三列：预览文本

                                # 处理空值，将空字符串转换为None
                                if voice_id == "" or voice_id is None:
                                    voice_id = None
                                if preview_text is None or np.isnan(preview_text):
                                    preview_text = ""

                                csv_config[filename] = {
                                    "voice_id": voice_id,
                                    "preview_text": preview_text,
                                }

                            st.success(f"成功导入 {len(csv_config)} 条配置")

                            # 应用CSV配置到文件
                            for i, file in enumerate(uploaded_files):
                                if file.name in csv_config:
                                    config = csv_config[file.name]
                                    if config["voice_id"]:
                                        custom_voice_ids[i] = config["voice_id"]
                                    if config["preview_text"]:
                                        custom_preview_texts[i] = config["preview_text"]
                        else:
                            st.error("CSV文件格式错误，需要至少包含文件名和音色ID两列")
                    except Exception as e:
                        st.error(f"CSV文件解析失败: {str(e)}")

                for i, file in enumerate(uploaded_files):
                    default_id = (
                        f"{base_voice_id}_{i+1}" if base_voice_id else f"voice_{i+1}"
                    )

                    # 音色ID输入
                    custom_id_value = custom_voice_ids.get(i, default_id)
                    custom_id = st.text_input(
                        f"音色ID {i+1}: {file.name}",
                        value=custom_id_value,
                        key=f"custom_id_{i}",
                    )
                    custom_voice_ids[i] = custom_id

                    # 预览文本输入
                    preview_text_value = custom_preview_texts.get(i, "")
                    preview_text = st.text_area(
                        f"预览文本 {i+1}: {file.name}",
                        value=preview_text_value,
                        height=68,
                        key=f"preview_text_{i}",
                        help="用于验证音色的文本，可选",
                    )
                    custom_preview_texts[i] = preview_text

            # 开始批量处理
            if st.button("🚀 开始批量克隆", type="primary"):
                if not base_voice_id and not any(custom_voice_ids.values()):
                    st.error("请设置基础音色ID或自定义音色ID")
                else:
                    # 验证所有音色ID
                    invalid_ids = []
                    for i, voice_id in custom_voice_ids.items():
                        if len(voice_id) < 8:
                            invalid_ids.append(f"文件 {i+1}: 音色ID太短")
                        elif not voice_id[0].isalpha():
                            invalid_ids.append(f"文件 {i+1}: 音色ID必须以字母开头")
                        elif not (
                            any(c.isalpha() for c in voice_id)
                            and any(c.isdigit() for c in voice_id)
                        ):
                            invalid_ids.append(f"文件 {i+1}: 音色ID必须包含字母和数字")

                    if invalid_ids:
                        for error in invalid_ids:
                            st.error(error)
                    else:
                        # 开始批量处理
                        progress_bar = st.progress(0)
                        status_text = st.empty()

                        success_count = 0
                        error_count = 0

                        for i, file in enumerate(uploaded_files):
                            status_text.text(
                                f"处理文件 {i+1}/{len(uploaded_files)}: {file.name}"
                            )

                            try:
                                # 保存文件到临时位置
                                with tempfile.NamedTemporaryFile(
                                    delete=False, suffix=f".{file.name.split('.')[-1]}"
                                ) as tmp_file:
                                    tmp_file.write(file.getvalue())
                                    tmp_path = tmp_file.name

                                # 上传文件
                                file_id = voice_manager.client.file_upload(tmp_path)

                                # 克隆音色
                                voice_id = custom_voice_ids[i]
                                preview_text = custom_preview_texts.get(i, None)
                                # 确保预览文本不是空字符串
                                if preview_text and preview_text.strip():
                                    preview_text = preview_text.strip()
                                else:
                                    preview_text = None

                                success = voice_manager.clone_voice(
                                    file_id=file_id,
                                    voice_id=voice_id,
                                    need_noise_reduction=need_noise_reduction,
                                    need_volume_normalization=need_volume_normalization,
                                    accuracy=accuracy,
                                    model=model,
                                    text=preview_text,
                                )

                                if success:
                                    success_count += 1
                                    st.success(f"✅ {file.name} -> {voice_id}")
                                else:
                                    error_count += 1
                                    st.error(f"❌ {file.name} -> {voice_id}")

                                # 清理临时文件
                                os.unlink(tmp_path)

                            except Exception as e:
                                error_count += 1
                                st.error(f"❌ {file.name}: {str(e)}")

                            # 更新进度
                            progress_bar.progress((i + 1) / len(uploaded_files))

                        status_text.text("批量处理完成！")
                        st.success(
                            f"批量处理完成！成功: {success_count}, 失败: {error_count}"
                        )

                        if success_count > 0:
                            st.info("克隆任务已提交！请稍后刷新音色列表查看状态。")


if __name__ == "__main__":
    # 读取tools/config.json，并将内容加入系统变量
    config_path = os.path.join(os.path.dirname(__file__), "config.json")
    if os.path.exists(config_path):
        with open(config_path, "r", encoding="utf-8") as f:
            config_data = json.load(f)
        for key, value in config_data.items():
            # 将所有配置项加入系统环境变量
            os.environ[str(key)] = str(value)

    main()
