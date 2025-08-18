import streamlit as st
import os
import sys
from pathlib import Path

import pandas as pd

# 添加当前目录到Python路径
current_dir = Path(__file__).parent
sys.path.insert(0, str(current_dir))

from utils import load_excel_data, convert_to_pinyin


def render_excel_manager():
    """渲染Excel管理器"""

    st.header("📖 Excel台本管理器")

    # --- 文件加载逻辑 ---
    # 路径设置
    tools_dir = Path(__file__).parent.parent
    example_excel_path = tools_dir / "example_voice_lines.xlsx"

    # 文件上传
    # --- 下载与加载示例 ---
    col1, col2 = st.columns([3, 1])
    with col1:
        uploaded_file = st.file_uploader(
            "📂 上传您自己的Excel台本文件",
            type=["xlsx", "xls"],
            help="上传后将自动加载数据，并替换当前表格",
        )

    with col2:
        if example_excel_path.exists():
            with open(example_excel_path, "rb") as f:
                st.download_button(
                    label="📥 下载表格示例（长空之王）",
                    data=f,
                    file_name="example_voice_lines.xlsx",
                    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                    help="下载一个包含示例台本的Excel文件",
                )
        if st.button(
            "🔄 加载示例台本（长空之王）", help="重新加载项目自带的示例Excel文件"
        ):
            if example_excel_path.exists():
                st.session_state.excel_data = load_excel_data(str(example_excel_path))
                st.session_state.excel_file_name = "示例文件"
                st.success("🔄 已加载示例台本")
                st.rerun()
            else:
                st.error("示例文件 'example_voice_lines.xlsx' 不存在！")
    # 处理文件加载
    if uploaded_file:
        try:
            st.session_state.excel_data = load_excel_data(uploaded_file)
            st.session_state.excel_file_name = uploaded_file.name
            st.success(f"✅ 已成功加载您上传的文件: {uploaded_file.name}")
        except Exception as e:
            st.error(f"加载文件失败: {e}")
            st.session_state.excel_data = pd.DataFrame()  # 清空数据
    else:
        # 如果session中没有数据，尝试加载示例文件
        if "excel_data" not in st.session_state:
            if example_excel_path.exists():
                st.session_state.excel_data = load_excel_data(example_excel_path)
                st.session_state.excel_file_name = "示例文件"
            else:
                st.session_state.excel_data = pd.DataFrame()
                st.session_state.excel_file_name = "无"

    st.divider()

    # --- 数据显示与交互 ---
    if "excel_data" in st.session_state and not st.session_state.excel_data.empty:
        df = st.session_state.excel_data
        file_name = st.session_state.get("excel_file_name", "未知文件")

        # 显示表格信息
        st.info(
            f"当前数据来源: **{file_name}** | 共 **{len(df)}** 行, **{len(df.columns)}** 列"
        )

        # 搜索功能
        col_search, col_clear = st.columns([3, 1])
        with col_search:
            excel_search = st.text_input(
                "🔍 搜索Excel数据",
                placeholder="输入关键词搜索任意列...",
                key="excel_search",
            )
        with col_clear:
            if excel_search:
                if st.button("🗑️ 清除搜索"):
                    st.session_state.excel_search = ""
                    st.rerun()

        # 时间码筛选功能
        timecode_input = st.text_input(
            "⏱️ 按时间码筛选",
            placeholder="例如: 00:01:23:12 (只显示此时间之后的内容)",
            key="excel_timecode_filter",
        )

        def timecode_to_frames(tc: str) -> int:
            try:
                h, m, s, f = map(int, tc.strip().split(":"))
                return ((h * 60 + m) * 60 + s) * 24 + f
            except (ValueError, IndexError):
                return -1

        # --- 数据过滤 ---
        filtered_df = df
        if timecode_input:
            input_frames = timecode_to_frames(timecode_input)
            if input_frames != -1:
                # 假设时间码在第一列
                filtered_df = filtered_df[
                    filtered_df.iloc[:, 0].apply(
                        lambda x: timecode_to_frames(str(x)) > input_frames
                    )
                ]
            else:
                st.warning("时间码格式不正确，请使用 HH:MM:SS:FF 格式。")

        if excel_search:
            search_term = excel_search.lower()
            filtered_df = filtered_df[
                filtered_df.apply(
                    lambda row: any(search_term in str(cell).lower() for cell in row),
                    axis=1,
                )
            ]

        # --- 表格显示 ---
        if not filtered_df.empty:
            st.subheader("点击行选择数据")

            # 展开/折叠
            if "excel_expanded" not in st.session_state:
                st.session_state.excel_expanded = False

            if st.button("📖 展开/折叠全部" if len(filtered_df) > 2 else "刷新"):
                st.session_state.excel_expanded = not st.session_state.excel_expanded

            display_limit = 50
            display_df = filtered_df
            if not st.session_state.excel_expanded:
                display_df = filtered_df.head(2)
            elif len(filtered_df) > display_limit:
                st.info(
                    f"数据过多，仅显示前 {display_limit} 行。请使用搜索功能缩小范围。"
                )
                display_df = filtered_df.head(display_limit)

            # --- 渲染行 ---
            for index, row in display_df.iterrows():
                with st.container():
                    cols = st.columns([1, 2, 2, 2, 3])
                    row_data = [
                        str(row.iloc[i]) if i < len(row) else "" for i in range(5)
                    ]

                    # 清理和准备数据
                    first_col_clean = row_data[0].replace(":", "").strip()
                    third_col = row_data[2]
                    # fifth_col = row_data[4] + " Ne t'inquiète pas"  # 添加固定文本
                    fifth_col = row_data[4]

                    # 显示列
                    with cols[0]:
                        st.write(f"**{first_col_clean}**")
                    with cols[1]:
                        st.write(row_data[1])
                    with cols[2]:
                        st.write(third_col)
                    with cols[3]:
                        st.write(row_data[3])
                    with cols[4]:
                        st.write(fifth_col)

                    # 选择按钮
                    if st.button(
                        f"🎯 选择第 {index + 1} 行", key=f"select_row_{index}"
                    ):
                        pinyin_text = convert_to_pinyin(third_col)
                        if pinyin_text:
                            st.session_state.test_voice_search = pinyin_text
                        st.session_state.test_text = fifth_col
                        st.session_state.file_prefix = first_col_clean
                        st.session_state.active_tab = "测试音色"
                        st.success(
                            f"已选择第 {index + 1} 行数据，请切换到“测试音色”标签页查看。"
                        )
                        st.rerun()

                    st.divider()
        else:
            st.warning("没有找到匹配的数据。")
    else:
        st.info("请上传一个Excel文件或加载示例台本以开始。")
