#!/usr/bin/env python3
"""
MiniMax Speech API 文件上传使用示例
"""

import os
import asyncio
from minimax_speech import MiniMaxSpeech, AsyncMiniMaxSpeech


def sync_file_upload_example():
    """同步文件上传示例"""
    print("=== 同步文件上传示例 ===")

    # 创建客户端
    client = MiniMaxSpeech(
        api_key=os.getenv("MINIMAX_API_KEY"), group_id=os.getenv("MINIMAX_GROUP_ID")
    )

    try:
        # 检查测试文件是否存在
        test_file = "test_audio.mp3"
        if not os.path.exists(test_file):
            print(f"❌ 测试文件不存在: {test_file}")
            print("请准备一个音频文件用于测试")
            return

        print(f"正在上传文件: {test_file}")

        # 上传文件
        file_id = client.file_upload(test_file, purpose="voice_clone")

        print("✅ 文件上传成功！")
        print(f"文件ID: {file_id}")

        # 获取文件信息（这里只是示例，实际API可能没有获取文件信息的接口）
        print(f"文件大小: {os.path.getsize(test_file)} 字节")

    except Exception as e:
        print(f"❌ 错误: {e}")
    finally:
        client.close()


async def async_file_upload_example():
    """异步文件上传示例"""
    print("\n=== 异步文件上传示例 ===")

    async with AsyncMiniMaxSpeech(
        api_key=os.getenv("MINIMAX_API_KEY"), group_id=os.getenv("MINIMAX_GROUP_ID")
    ) as client:
        try:
            # 检查测试文件是否存在
            test_file = "test_audio.mp3"
            if not os.path.exists(test_file):
                print(f"❌ 测试文件不存在: {test_file}")
                print("请准备一个音频文件用于测试")
                return

            print(f"正在异步上传文件: {test_file}")

            # 上传文件
            file_id = await client.file_upload(test_file, purpose="voice_clone")

            print("✅ 异步文件上传成功！")
            print(f"文件ID: {file_id}")

        except Exception as e:
            print(f"❌ 错误: {e}")


def batch_file_upload_example():
    """批量文件上传示例"""
    print("\n=== 批量文件上传示例 ===")

    client = MiniMaxSpeech(
        api_key=os.getenv("MINIMAX_API_KEY"), group_id=os.getenv("MINIMAX_GROUP_ID")
    )

    try:
        # 模拟多个文件
        test_files = ["audio1.mp3", "audio2.mp3", "audio3.mp3"]

        # 过滤存在的文件
        existing_files = [f for f in test_files if os.path.exists(f)]

        if not existing_files:
            print("❌ 没有找到可用的测试文件")
            print("请准备音频文件用于测试")
            return

        print(f"找到 {len(existing_files)} 个文件，开始批量上传...")

        file_ids = []
        for i, file_path in enumerate(existing_files, 1):
            try:
                print(f"上传文件 {i}/{len(existing_files)}: {file_path}")
                file_id = client.file_upload(file_path, purpose="voice_clone")
                file_ids.append(file_id)
                print(f"✅ 文件 {file_path} 上传成功，ID: {file_id}")
            except Exception as e:
                print(f"❌ 文件 {file_path} 上传失败: {e}")

        print("\n批量上传完成！")
        print(f"成功上传: {len(file_ids)} 个文件")
        print(f"文件ID列表: {file_ids}")

    except Exception as e:
        print(f"❌ 错误: {e}")
    finally:
        client.close()


def file_upload_with_validation_example():
    """带验证的文件上传示例"""
    print("\n=== 带验证的文件上传示例 ===")

    client = MiniMaxSpeech(
        api_key=os.getenv("MINIMAX_API_KEY"), group_id=os.getenv("MINIMAX_GROUP_ID")
    )

    try:
        test_file = "ICE_10s.wav"

        # 文件存在性验证
        if not os.path.exists(test_file):
            raise FileNotFoundError(f"文件不存在: {test_file}")

        # 文件大小验证（假设最大50MB）
        file_size = os.path.getsize(test_file)
        max_size = 50 * 1024 * 1024  # 50MB

        if file_size > max_size:
            raise ValueError(f"文件过大: {file_size} 字节，最大允许 {max_size} 字节")

        # 文件类型验证
        allowed_extensions = [".mp3", ".wav", ".m4a", ".flac"]
        file_ext = os.path.splitext(test_file)[1].lower()

        if file_ext not in allowed_extensions:
            raise ValueError(
                f"不支持的文件类型: {file_ext}，支持的类型: {allowed_extensions}"
            )

        print("文件验证通过:")
        print(f"  文件名: {test_file}")
        print(f"  文件大小: {file_size} 字节")
        print(f"  文件类型: {file_ext}")

        # 上传文件
        file_id = client.file_upload(test_file, purpose="voice_clone")

        print(f"✅ 文件上传成功！文件ID: {file_id}")

    except Exception as e:
        print(f"❌ 错误: {e}")
    finally:
        client.close()


if __name__ == "__main__":
    # 检查环境变量
    if not os.getenv("MINIMAX_API_KEY") or not os.getenv("MINIMAX_GROUP_ID"):
        print("❌ 请设置环境变量 MINIMAX_API_KEY 和 MINIMAX_GROUP_ID")
        print("   可以使用 set_env.ps1 脚本设置环境变量")
        exit(1)

    # 运行同步示例
    sync_file_upload_example()

    # 运行异步示例
    asyncio.run(async_file_upload_example())

    # 运行批量上传示例
    batch_file_upload_example()

    # 运行带验证的示例
    file_upload_with_validation_example()

    print("\n✅ 所有示例运行完成！")

