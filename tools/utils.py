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
