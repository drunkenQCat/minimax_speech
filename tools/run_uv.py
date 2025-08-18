#!/usr/bin/env python3
"""
使用 uv 启动 MiniMax 音色管理器
"""

import subprocess
import sys
from pathlib import Path


def main():
    """使用 uv 启动 Streamlit 应用"""
    # 获取当前脚本所在目录
    current_dir = Path(__file__).parent

    # 切换到项目根目录
    project_root = current_dir.parent

    print("🚀 使用 uv 启动 MiniMax 音色管理器...")
    print(f"📁 项目根目录: {project_root}")
    print("🌐 浏览器将自动打开 http://localhost:8501")
    print("⏹️  按 Ctrl+C 停止应用")
    print("-" * 50)

    try:
        # 使用 uv run 启动应用
        subprocess.run(
            [
                "uv",
                "run",
                "streamlit",
                "run",
                str(current_dir / "app.py"),
                "--server.port",
                "8501",
                "--server.address",
                "0.0.0.0",
            ],
            cwd=project_root,
        )
    except KeyboardInterrupt:
        print("\n👋 应用已停止")
    except FileNotFoundError:
        print("❌ 错误: 未找到 uv 命令")
        print(
            "请确保已安装 uv: https://docs.astral.sh/uv/getting-started/installation/"
        )
        sys.exit(1)


if __name__ == "__main__":
    main()

