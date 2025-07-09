#!/usr/bin/env python3
"""
MiniMax Speech API 语音克隆使用示例
"""

import os
import asyncio
from minimax_speech import (
    MiniMaxSpeech,
    AsyncMiniMaxSpeech,
    VoiceCloneRequest,
    VoiceCloneResponse,
)


def create_and_delete_voice():
    """创建并删除语音"""
    client = MiniMaxSpeech(
        api_key=os.getenv("MINIMAX_API_KEY"), group_id=os.getenv("MINIMAX_GROUP_ID")
    )

    client.voice_delete("TestVoice001")
    file_id = client.file_upload("ICE_10s.wav", purpose="voice_clone")
    client.voice_clone_simple(file_id=file_id, voice_id="TestVoice001", text="嗯，你确定这个地方能通到影院吗？什么打算？你这次电影票不会又买错了吧？这门推不开！", model="speech-01-turbo", accuracy=0.8, need_volume_normalization=True)
    client.voice_delete("TestVoice001")
    client.close()

def sync_voice_clone_example():
    """同步语音克隆示例"""
    print("=== 同步语音克隆示例 ===")

    # 创建客户端
    client = MiniMaxSpeech(
        api_key=os.getenv("MINIMAX_API_KEY"), group_id=os.getenv("MINIMAX_GROUP_ID")
    )

    try:
        # 首先上传音频文件
        print("1. 上传音频文件并删除MyVoice001...")
        file_id = client.file_upload("ICE_10s.wav", purpose="voice_clone")
        print(f"   文件上传成功，文件ID: {file_id}")
        __import__("ipdb").set_trace()
        client.voice_delete("MyVoice001")
        print("   已删除MyVoice001")

        # 创建语音克隆请求
        print("\n2. 创建语音克隆请求...")
        request = VoiceCloneRequest(
            file_id=file_id,
            voice_id="MyVoice001",  # 必须至少8个字符，包含字母和数字，以字母开头
            need_noise_reduction=False,
            model="speech-02-hd",
            accuracy=0.8,
            need_volume_normalization=True,
        )

        print(f"   请求参数:")
        print(f"     文件ID: {request.file_id}")
        print(f"     语音ID: {request.voice_id}")
        print(f"     降噪: {request.need_noise_reduction}")
        print(f"     预览文本: {request.text}")
        print(f"     模型: {request.model}")
        print(f"     精度: {request.accuracy}")
        print(f"     音量标准化: {request.need_volume_normalization}")

        # 执行语音克隆
        print("\n3. 执行语音克隆...")
        __import__("ipdb").set_trace()
        response = client.voice_clone(request)

        print("✅ 语音克隆成功！")
        print(f"   输入敏感: {response.input_sensitive}")
        print(f"   状态码: {response.base_resp.status_code}")
        print(f"   状态消息: {response.base_resp.status_msg}")

    except Exception as e:
        print(f"❌ 错误: {e}")
    finally:
        client.close()


async def async_voice_clone_example():
    """异步语音克隆示例"""
    print("\n=== 异步语音克隆示例 ===")

    async with AsyncMiniMaxSpeech(
        api_key=os.getenv("MINIMAX_API_KEY"), group_id=os.getenv("MINIMAX_GROUP_ID")
    ) as client:
        try:
            # 首先上传音频文件
            print("1. 上传音频文件...")
            file_id = await client.file_upload("test_audio.mp3", purpose="voice_clone")
            print(f"   文件上传成功，文件ID: {file_id}")

            # 使用简化接口进行语音克隆
            print("\n2. 使用简化接口进行语音克隆...")
            response = await client.voice_clone_simple(
                file_id=file_id,
                voice_id="AsyncVoice001",
                need_noise_reduction=False,
                text="这是异步语音克隆的测试。",
                model="speech-01-turbo",
                accuracy=0.7,
                need_volume_normalization=False,
            )

            print("✅ 异步语音克隆成功！")
            print(f"   输入敏感: {response.input_sensitive}")
            print(f"   状态码: {response.base_resp.status_code}")
            print(f"   状态消息: {response.base_resp.status_msg}")

        except Exception as e:
            print(f"❌ 错误: {e}")


def voice_clone_validation_example():
    """语音克隆验证示例"""
    print("\n=== 语音克隆验证示例 ===")

    client = MiniMaxSpeech(
        api_key=os.getenv("MINIMAX_API_KEY"), group_id=os.getenv("MINIMAX_GROUP_ID")
    )

    try:
        # 测试无效的voice_id
        print("1. 测试无效的voice_id...")
        try:
            file_id = client.file_upload("ICE_10s.wav", purpose="voice_clone")
            request = VoiceCloneRequest(
                file_id=file_id,
                voice_id="123",  # 太短，且不以字母开头
                text="测试",
            )
            client.voice_clone(request)
        except ValueError as e:
            print(f"   ✅ 正确捕获错误: {e}")

        # 测试无效的voice_id格式
        print("\n2. 测试无效的voice_id格式...")
        try:
            request = VoiceCloneRequest(
                file_id=10011,
                voice_id="abcdefgh",  # 只包含字母，没有数字
                text="测试",
            )
            client.voice_clone(request)
        except ValueError as e:
            print(f"   ✅ 正确捕获错误: {e}")

        # 测试过长的text
        print("\n3. 测试过长的text...")
        try:
            long_text = "a" * 2500  # 超过2000字符
            file_id = client.file_upload("ICE_10s.wav", purpose="voice_clone")
            request = VoiceCloneRequest(
                file_id=file_id, voice_id="ValidVoice001", text=long_text
            )
            client.voice_clone(request)
        except ValueError as e:
            print(f"   ✅ 正确捕获错误: {e}")

        # 测试无效的accuracy
        print("\n4. 测试无效的accuracy...")
        try:
            request = VoiceCloneRequest(
                file_id=288043710128213,
                voice_id="ValidVoice001",
                accuracy=1.5,  # 超出范围[0,1]
            )
            client.voice_clone(request)
        except ValueError as e:
            print(f"   ✅ 正确捕获错误: {e}")

        # 测试无效的model
        print("\n5. 测试无效的model...")
        try:
            request = VoiceCloneRequest(
                file_id=288043710128213, voice_id="ValidVoice001", model="invalid-model"
            )
            client.voice_clone(request)
        except ValueError as e:
            print(f"   ✅ 正确捕获错误: {e}")

        print("\n✅ 所有验证测试通过！")

    except Exception as e:
        print(f"❌ 错误: {e}")
    finally:
        client.close()


def voice_clone_workflow_example():
    """语音克隆完整工作流示例"""
    print("\n=== 语音克隆完整工作流示例 ===")

    client = MiniMaxSpeech(
        api_key=os.getenv("MINIMAX_API_KEY"), group_id=os.getenv("MINIMAX_GROUP_ID")
    )

    try:
        # 步骤1: 上传音频文件
        print("步骤1: 上传音频文件")
        file_id = client.file_upload("test_audio.mp3", purpose="voice_clone")
        print(f"   文件ID: {file_id}")

        # 步骤2: 创建语音克隆
        print("\n步骤2: 创建语音克隆")
        response = client.voice_clone_simple(
            file_id=file_id,
            voice_id="WorkflowVoice001",
            need_noise_reduction=True,
            text="这是完整工作流的测试。",
            model="speech-02-hd",
            accuracy=0.8,
            need_volume_normalization=True,
        )
        print(f"   克隆状态: {response.base_resp.status_msg}")
        print(f"   输入敏感: {response.input_sensitive}")

        # 步骤3: 使用克隆的语音进行T2A
        print("\n步骤3: 使用克隆的语音进行T2A")
        t2a_response = client.text_to_speech_simple(
            text="现在使用克隆的语音生成新的音频内容。",
            voice_id="WorkflowVoice001",  # 使用克隆的语音ID
            model="speech-02-hd",
        )

        # 保存生成的音频
        import binascii

        audio_bytes = binascii.unhexlify(t2a_response.data.audio)
        with open("cloned_voice_output.mp3", "wb") as f:
            f.write(audio_bytes)

        print(f"   生成的音频已保存: cloned_voice_output.mp3")
        print(f"   音频时长: {t2a_response.extra_info.audio_length} 毫秒")
        print(f"   计费字符数: {t2a_response.extra_info.usage_characters}")

        print("\n✅ 完整工作流执行成功！")

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

    # 检查测试文件是否存在
    if not os.path.exists("test_audio.mp3"):
        print("❌ 测试文件 test_audio.mp3 不存在")
        print("   请准备一个音频文件用于测试")
        exit(1)

    if not os.path.exists("ICE_10s.wav"):
        print("❌ 测试文件 ICE_10s.wav 不存在")
        print("   请准备一个音频文件用于测试")
        exit(1)
    # 运行同步示例
    __import__("ipdb").set_trace()
    # sync_voice_clone_example()
    create_and_delete_voice()

    # 运行异步示例
    # asyncio.run(async_voice_clone_example())

    # 运行验证示例
    # voice_clone_validation_example()

    # 运行完整工作流示例
    # voice_clone_workflow_example()

    print("\n✅ 所有示例运行完成！")

