"""
MiniMax 音色管理工具
基于 Streamlit 的 Web 界面，用于管理 MiniMax 音色
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

# from pathlib import Path
# import sys
from minimax_speech import MiniMaxSpeech
from minimax_speech.tts_models import T2AResponse, Voice, Language
from minimax_speech.voice_query_models import SystemVoice, VoiceCloning


# 添加项目根目录到 Python 路径
# project_root = Path(__file__).parent.parent
# sys.path.insert(0, str(project_root))


def generate_safe_filename(st: str) -> str:
    """根据句子内容生成新的文件名。

    参数:
        st (Sentence): 句子对象。

    返回:
        FileInfo: 文件信息对象。
    """
    # 生成文件名
    # 使用str.translate去除所有不可见的控制字符（包括\r, \n, \t等）
    control_chars = "".join(map(chr, range(0, 32))) + chr(127)
    safe_file_name = st.translate({ord(c): None for c in control_chars})
    # 去掉文件名中的非法字符
    safe_file_name = re.sub(r'[<>:"/\\|?*]', "", safe_file_name)
    if len(safe_file_name) > 15:
        safe_file_name = safe_file_name[:15]
        post_fix = hashlib.md5(str(time.time()).encode()).hexdigest()[:4]
        safe_file_name = f"{safe_file_name}_{post_fix}"
        return safe_file_name
    else:
        return safe_file_name


def convert_to_pinyin(text: str) -> str:
    """将中文文本转换为拼音"""
    if not text or not isinstance(text, str):
        return ""

    try:
        # 转换为拼音，使用NORMAL风格（不带声调）
        pinyin_list = pinyin(text, style=Style.NORMAL)
        # 将拼音列表连接成字符串
        return "".join([p[0] for p in pinyin_list if p[0]])
    except Exception as e:
        st.error(f"拼音转换失败: {str(e)}")
        return text


def load_excel_data(file_path: str) -> pd.DataFrame:
    """加载Excel文件数据"""
    try:
        # 读取Excel文件
        df = pd.read_excel(file_path, engine="openpyxl")
        return df
    except Exception as e:
        st.error(f"加载Excel文件失败: {str(e)}")
        return pd.DataFrame()


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


def main():
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
    voice_manager.get_voices(force_refresh=True)
    st.success("音色列表已刷新！")

    # Excel表格加载和显示
    st.header("📊 法语剧本数据")

    # Excel文件路径
    excel_path = r"X:\Projects\长空之王法语_250707\01-Originals\《长空之王》中法语完整及两段0621_法语润稿_0716更新.xlsx"

    # 检查文件是否存在
    if os.path.exists(excel_path):
        # 加载Excel数据
        if "excel_data" not in st.session_state:
            st.session_state.excel_data = load_excel_data(excel_path)

        df = st.session_state.excel_data

        if not df.empty:
            # 显示表格信息
            st.info(f"📋 已加载 {len(df)} 行数据，共 {len(df.columns)} 列")

            # 搜索功能
            col_search, col_clear = st.columns([3, 1])

            with col_search:
                excel_search = st.text_input(
                    "🔍 搜索Excel数据",
                    placeholder="输入关键词搜索任意列...",
                    help="支持搜索任意列的内容，支持中文、拼音、法语等",
                    key="excel_search",
                )

            with col_clear:
                if excel_search:
                    if st.button("🗑️ 清除搜索", help="清除搜索条件，显示所有数据"):
                        if "excel_search" in st.session_state:
                            del st.session_state.excel_search
                        st.rerun()

            # 时间码筛选功能
            col_timecode, col_timecode_tip = st.columns([2, 2])
            with col_timecode:
                timecode_input = st.text_input(
                    "⏱️ 时间码筛选 (24帧)",
                    placeholder="如 00:01:23:12",
                    help="输入24帧制时间码，只显示起始时间码大于该值的行",
                    key="excel_timecode_filter",
                )
            with col_timecode_tip:
                st.caption("格式: 时:分:秒:帧 (如 00:01:23:12)，留空不过滤")

            def timecode_to_frames(tc: str) -> int:
                """将时间码(00:00:00:00)转为帧数(24帧制)"""
                try:
                    h, m, s, f = [int(x) for x in tc.strip().split(":")]
                    return ((h * 60 + m) * 60 + s) * 24 + f
                except Exception:
                    return -1

            # 过滤数据
            filtered_df = df
            # 时间码过滤
            if timecode_input:
                input_frames = timecode_to_frames(timecode_input)
                if input_frames is None:
                    st.warning("时间码格式错误，应为 00:00:00:00")
                else:
                    # 假设起始时间码在第一列（索引0）
                    def row_timecode_gt(row):
                        tc = str(row.iloc[0]) if len(row) > 0 else ""
                        tc_frames = timecode_to_frames(tc)
                        return tc_frames is not None and tc_frames > input_frames

                    filtered_df = filtered_df[
                        filtered_df.apply(row_timecode_gt, axis=1)
                    ]

            # 搜索功能
            if excel_search:
                # 在所有列中搜索
                filtered_df = filtered_df[
                    filtered_df.apply(
                        lambda row: any(
                            excel_search.lower() in str(cell).lower()
                            for cell in row
                            if pd.notna(cell)
                        ),
                        axis=1,
                    )
                ]

                if not filtered_df.empty:
                    st.success(
                        f"🔍 搜索 '{excel_search}' 找到 {len(filtered_df)} 行匹配数据"
                    )
                else:
                    st.warning(f"🔍 搜索 '{excel_search}' 没有找到匹配的数据")
            else:
                filtered_df = df
                st.info("💡 输入搜索关键词来过滤数据，避免页面卡顿")

            # 显示表格（可点击）
            if not filtered_df.empty:
                st.subheader("点击行选择数据")

                # 默认显示2行，支持展开/折叠
                default_display_rows = 2
                max_display_rows = 50
                total_rows = len(filtered_df)

                # 展开/折叠状态
                if "excel_expanded" not in st.session_state:
                    st.session_state.excel_expanded = False

                # 只在有超过2行时显示展开按钮
                if total_rows > default_display_rows:
                    col_expand, col_info = st.columns([1, 3])
                    with col_expand:
                        if st.button(
                            (
                                "📖 展开全部"
                                if not st.session_state.excel_expanded
                                else "📚 折叠"
                            ),
                            help="展开或折叠表格数据",
                        ):
                            st.session_state.excel_expanded = (
                                not st.session_state.excel_expanded
                            )
                            st.rerun()
                    with col_info:
                        if st.session_state.excel_expanded:
                            if total_rows > max_display_rows:
                                st.info(
                                    f"📊 显示前 {max_display_rows} 行，共 {total_rows} 行数据。请使用搜索进一步缩小范围。"
                                )
                            else:
                                st.info(f"📊 显示全部 {total_rows} 行数据")
                        else:
                            st.info(
                                f"📊 默认仅显示前 {default_display_rows} 行，共 {total_rows} 行数据"
                            )

                # 决定实际显示的DataFrame
                if st.session_state.excel_expanded:
                    if total_rows > max_display_rows:
                        display_df = filtered_df.head(max_display_rows)
                    else:
                        display_df = filtered_df
                else:
                    display_df = filtered_df.head(default_display_rows)

                # 为每行添加点击功能
                for index, row in display_df.iterrows():
                    # 创建行容器
                    with st.container():
                        col1, col2, col3, col4, col5 = st.columns([1, 2, 2, 2, 3])

                        with col1:
                            # 第一列：序号（去掉冒号）
                            first_col = str(row.iloc[0]) if len(row) > 0 else ""
                            first_col_clean = first_col.replace(":", "").strip()
                            st.write(f"**{first_col_clean}**")

                        with col2:
                            # 第二列
                            second_col = str(row.iloc[1]) if len(row) > 1 else ""
                            st.write(
                                second_col[:50] + "..."
                                if len(second_col) > 50
                                else second_col
                            )

                        with col3:
                            # 第三列（中文，用于生成拼音）
                            third_col = str(row.iloc[2]) if len(row) > 2 else ""
                            st.write(
                                third_col[:50] + "..."
                                if len(third_col) > 50
                                else third_col
                            )

                        with col4:
                            # 第四列
                            fourth_col = str(row.iloc[3]) if len(row) > 3 else ""
                            st.write(
                                fourth_col[:50] + "..."
                                if len(fourth_col) > 50
                                else fourth_col
                            )

                        with col5:
                            # 第五列（测试文本）
                            fifth_col = str(row.iloc[4]) if len(row) > 4 else ""
                            fifth_col = fifth_col + "Ne t'inquiète pas"
                            st.write(
                                fifth_col[:80] + "..."
                                if len(fifth_col) > 80
                                else fifth_col
                            )

                        # 添加点击按钮
                        if st.button(
                            f"🎯 选择第 {index + 1} 行", key=f"select_row_{index}"
                        ):
                            # 处理点击事件
                            # 1. 将第三列转换为拼音并搜索音色
                            pinyin_text = convert_to_pinyin(third_col)
                            if pinyin_text:
                                # 设置搜索关键词
                                st.session_state.test_voice_search = pinyin_text

                            # 2. 将第五列填入测试文本
                            st.session_state.test_text = fifth_col

                            # 3. 保存第一列信息用于文件名
                            st.session_state.file_prefix = first_col_clean

                            # 跳转到测试音色标签页
                            st.session_state.active_tab = "测试音色"
                            st.success(f"已选择第 {index + 1} 行数据")
                            st.rerun()

                        st.divider()
            else:
                st.info("没有数据可显示，请尝试其他搜索条件")
        else:
            st.error("Excel文件为空或格式不正确")
    else:
        st.error(f"Excel文件不存在: {excel_path}")
        st.info("请检查文件路径是否正确")

    # 侧边栏配置
    with st.sidebar:

        with st.expander("🔧 配置", expanded=False):
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
        ["🎤 测试音色", "📋 音色列表", "🎭 系统音色", "➕ 添加音色", "📁 批量上传"]
    )

    # 标签页1: 测试音色
    with tab1:
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
                st.info(
                    f"🎯 快速测试模式：已选择音色 {st.session_state.quick_test_voice}"
                )
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

        voices = voice_manager.get_voices()

        if not voices:
            st.info("暂无可用音色进行测试")
        else:
            col1, col2 = st.columns(2)

            with col1:
                # 搜索音色
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
                    if search_voice:
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
                    else:
                        st.warning(f"🔍 搜索 '{search_voice}' 没有找到匹配的音色")

                # 选择音色
                voice_options = {
                    f"{v.voice_id} ({v.description or '未命名'})": v.voice_id
                    for v in filtered_test_voices
                }

                if voice_options:
                    # 根据搜索结果调整下拉菜单的提示
                    if search_voice and filtered_test_voices:
                        selectbox_label = (
                            f"🎯 选择音色 (找到 {len(filtered_test_voices)} 个匹配结果)"
                        )
                        selectbox_help = f"搜索结果：'{search_voice}' 匹配到 {len(filtered_test_voices)} 个音色"
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
                        for i, (display_name, voice_id) in enumerate(
                            voice_options.items()
                        ):
                            if voice_id == quick_test_voice_id:
                                default_index = i
                                break

                    selected_voice = st.selectbox(
                        selectbox_label,
                        options=list(voice_options.keys()),
                        index=default_index,
                        help=selectbox_help,
                    )

                    # 测试文本
                    test_text = st.text_area(
                        "测试文本",
                        value=st.session_state.get(
                            "test_text",
                            "你好，这是一个测试音频。Hello, this is a test audio.",
                        ),
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

                    # 语言增强参数
                    language_boost = st.selectbox(
                        "语言增强",
                        options=[
                            "无",
                            "Chinese",
                            "English",
                            "French",
                            "German",
                            "Spanish",
                            "Italian",
                            "Japanese",
                            "Korean",
                            "Russian",
                            "Arabic",
                            "Portuguese",
                            "Turkish",
                            "Dutch",
                            "Ukrainian",
                            "Vietnamese",
                            "Indonesian",
                            "Thai",
                            "Polish",
                            "Romanian",
                            "Greek",
                            "Czech",
                            "Finnish",
                            "Hindi",
                            "auto",
                        ],
                        help="选择语言增强，提高特定语言的发音质量",
                    )

                    # 将"无"转换为None
                    emotion_value = None if emotion == "无" else emotion
                    language_boost_value = (
                        None if language_boost == "无" else language_boost
                    )

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
                                    language_boost=language_boost_value,
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

                                        # 清除快速测试状态
                                        if "quick_test_voice" in st.session_state:
                                            del st.session_state.quick_test_voice

                                        safe_test_text = generate_safe_filename(
                                            test_text
                                        )
                                        # 提供下载链接
                                        with open(tmp_path, "rb") as f:
                                            # 获取文件名前缀
                                            file_prefix = st.session_state.get(
                                                "file_prefix", ""
                                            )
                                            if file_prefix:
                                                download_filename = f"{file_prefix}_{voice_options[selected_voice]}_{safe_test_text}.mp3"
                                            else:
                                                download_filename = f"{voice_options[selected_voice]}_{safe_test_text}.mp3"

                                            st.download_button(
                                                label="📥 下载音频",
                                                data=f.read(),
                                                file_name=download_filename,
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

    # 标签页2: 音色列表
    with tab2:
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
                            "", value=is_checked, key=f"check_{voice.voice_id}"
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
                            if st.button(
                                "✅ 确认删除", key=f"confirm_{voice.voice_id}"
                            ):
                                voice_manager.delete_voice(voice.voice_id)
                                st.session_state.confirm_delete_id = None
                                st.rerun()
                        with col_c2:
                            if st.button("❌ 取消", key=f"cancel_{voice.voice_id}"):
                                st.session_state.confirm_delete_id = None
                    st.divider()

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
                                        def __init__(
                                            self, voice_id, name, description=""
                                        ):
                                            self.value = voice_id
                                            self.name = name
                                            self.description = description

                                    api_voice = APIVoice(
                                        voice_id=voice_info.voice_id,
                                        name=voice_info.voice_name
                                        or voice_info.voice_id,
                                        description=voice_info.description or "",
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
                key="search_term",
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
            filtered_voices = []
            search_lower = search_term.lower()  # 提前转换大小写避免重复计算

            for voice in system_voices:
                # 检查主要属性
                matches_value = search_lower in voice.value.lower()
                matches_name = search_lower in voice.name.lower()

                # 检查可选属性
                matches_description = False
                if hasattr(voice, "description") and voice.description:
                    # 只检查第一个描述（根据原逻辑）
                    if (
                        voice.description[0]
                        and search_lower in voice.description[0].lower()
                    ):
                        matches_description = True

                # 任一条件匹配则包含
                if matches_value or matches_name or matches_description:
                    filtered_voices.append(voice)
        else:
            filtered_voices = system_voices

        # 显示当前音色来源和搜索状态
        if search_term:
            if filtered_voices:
                st.success(
                    f"🔍 搜索 '{search_term}' 找到 {len(filtered_voices)} 个匹配音色 ↓ 请在下拉菜单中选择"
                )
            else:
                st.warning(f"🔍 搜索 '{search_term}' 没有找到匹配的音色")
        else:
            if st.session_state.api_system_voices:
                st.info(
                    f"📊 当前显示 {len(system_voices)} 个音色（基础 {len(base_system_voices)} + API {len(st.session_state.api_system_voices)}）"
                )
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
                    if hasattr(voice, "description") and voice.description:
                        display_name = (
                            f"{voice.value} ({voice.name}) - {voice.description}"
                        )
                    else:
                        display_name = f"{voice.value} ({voice.name})"
                    voice_options[display_name] = voice.value

                # 根据搜索结果调整下拉菜单的提示
                if search_term and filtered_voices:
                    selectbox_label = (
                        f"🎯 选择系统音色 (找到 {len(filtered_voices)} 个匹配结果)"
                    )
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
                        key="sys_model",
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
                    key="sys_emotion",
                )

                # 语言增强参数
                language_boost = st.selectbox(
                    "语言增强",
                    options=[
                        "无",
                        "Chinese",
                        "English",
                        "French",
                        "German",
                        "Spanish",
                        "Italian",
                        "Japanese",
                        "Korean",
                        "Russian",
                        "Arabic",
                        "Portuguese",
                        "Turkish",
                        "Dutch",
                        "Ukrainian",
                        "Vietnamese",
                        "Indonesian",
                        "Thai",
                        "Polish",
                        "Romanian",
                        "Greek",
                        "Czech",
                        "Finnish",
                        "Hindi",
                        "auto",
                    ],
                    help="选择语言增强，提高特定语言的发音质量",
                    key="sys_language_boost",
                )

                # 将"无"转换为None
                emotion_value = None if emotion == "无" else emotion
                language_boost_value = (
                    None if language_boost == "无" else language_boost
                )

                if st.button("🎵 生成测试音频", type="primary", key="sys_generate"):
                    if test_text.strip():
                        # TODO
                        safe_test_text = generate_safe_filename(test_text)
                        with st.spinner("正在生成音频..."):
                            result = voice_manager.test_voice(
                                voice_id=voice_options[selected_voice],
                                text=test_text,
                                speed=speed,
                                volume=volume,
                                pitch=pitch,
                                emotion=emotion_value,
                                language_boost=language_boost_value,
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
                                        test_text.strip()
                                        st.download_button(
                                            label="📥 下载音频",
                                            data=f.read(),
                                            file_name=f"{voice_options[selected_voice]}_{safe_test_text}.mp3",
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
                
                **音频参数：**
                - 语速: 0.5-2.0，1.0为正常速度
                - 音量: 0-10，1.0为正常音量
                - 音调: -12到12，0为正常音调
                - 情感: 选择语音的情感表达
                - 语言增强: 提高特定语言的发音质量
                
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
                    if hasattr(voice, "description") and voice.description:
                        description = voice.description
                    elif hasattr(voice, "name"):
                        description = voice.name

                    voice_list.append(
                        {
                            "音色ID": voice.value,
                            "描述": description,
                            "来源": (
                                "API"
                                if voice in st.session_state.api_system_voices
                                else "基础"
                            ),
                        }
                    )

                # 创建可滚动的音色列表
                voice_df = pd.DataFrame(voice_list)
                st.dataframe(voice_df, use_container_width=True, hide_index=True)

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
