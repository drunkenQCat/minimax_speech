"""
批量上传页面
"""

import streamlit as st
import os
import tempfile

import numpy as np
import pandas as pd
import io

# from pathlib import Path
# import sys

import sys
from pathlib import Path

# 添加components目录到Python路径
components_dir = Path(__file__).parent.parent / "components"
sys.path.insert(0, str(components_dir))

from components.voice_manager import VoiceManager


def render_batch_upload(voice_manager: VoiceManager):
    """渲染批量上传页面"""
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

