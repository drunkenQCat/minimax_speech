"""
添加音色页面
"""

import os
import tempfile
import streamlit as st
import sys
from pathlib import Path

# 添加components目录到Python路径
components_dir = Path(__file__).parent.parent / "components"
sys.path.insert(0, str(components_dir))

from components.voice_manager import VoiceManager


def render_add_voice(voice_manager: VoiceManager):
    """渲染添加音色页面"""
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

