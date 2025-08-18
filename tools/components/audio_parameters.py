import streamlit as st
import os
import tempfile
import binascii


import sys
from pathlib import Path

# 添加components目录到Python路径
components_dir = Path(__file__).parent.parent / "components"
sys.path.insert(0, str(components_dir))

from components.voice_manager import VoiceManager
from utils import generate_safe_filename


def render_audio_parameters(voice_manager: VoiceManager):
    voice_options = st.session_state.get("voice_options", {})
    selected_voice_num = st.session_state.get("selected_clone_voice_num", "")
    voice_id = voice_options.get(selected_voice_num, "") if voice_options else ""
    # 音频参数

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
    language_boost_value = None if language_boost == "无" else language_boost

    if st.button("🎵 生成测试音频", type="primary"):
        test_text = st.session_state.test_text
        if not test_text.strip():
            st.warning("请输入测试文本")
            return
        with st.spinner("正在生成音频..."):
            result = voice_manager.test_voice(
                voice_id=voice_manager.current_voice,
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

            if not result:
                st.error("生成音频失败，请检查参数设置或网络连接")
                return
            # 保存音频文件
            audio_data = result.data.audio
            audio_data = binascii.unhexlify(audio_data)
            if not audio_data:
                st.error("生成的音频数据为空，请检查参数设置或网络连接")
                return
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

            safe_test_text = generate_safe_filename(test_text)
            # 提供下载链接
            with open(tmp_path, "rb") as f:
                # 获取文件名前缀
                file_prefix = st.session_state.get("file_prefix", "")
                if file_prefix:
                    download_filename = f"{file_prefix}_{voice_id}_{safe_test_text}.mp3"
                else:
                    download_filename = f"{voice_id}_{safe_test_text}.mp3"

                st.download_button(
                    label="📥 下载音频",
                    data=f.read(),
                    file_name=download_filename,
                    mime="audio/mp3",
                )

            # 清理临时文件
            os.unlink(tmp_path)
