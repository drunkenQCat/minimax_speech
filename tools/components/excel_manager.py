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

    # Excel表格加载和显示

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
