"""
MiniMax Speech API 基本使用示例
"""

import os
import binascii
from minimax_speech import MiniMaxSpeech, T2ARequest, VoiceSetting, AudioSetting
from minimax_speech.tts_models import Voice


def main():
    """基本使用示例"""

    # 设置API密钥（也可以通过环境变量MINIMAX_API_KEY设置）
    api_key = os.getenv("MINIMAX_API_KEY")
    group_id = os.getenv("MINIMAX_GROUP_ID")

    if not api_key:
        print("请设置环境变量 MINIMAX_API_KEY")
        return

    if not group_id:
        print("请设置环境变量 MINIMAX_GROUP_ID")
        return

    # 创建客户端
    client = MiniMaxSpeech(api_key=api_key, group_id=group_id)

    try:
        # 示例1: 中文文本转语音
        print("示例1: 中文文本转语音")

        voice_setting = VoiceSetting(
            voice_id="MyVoice001",
            speed=1.0,
            vol=1.0,
            pitch=0,
        )

        audio_setting = AudioSetting(sample_rate=44100, bitrate=256000, format="mp3")

        chinese_request = T2ARequest(
            model="speech-02-hd",
            text="你好，世界！欢迎使用MiniMax语音API。",
            voice_setting=voice_setting,
            audio_setting=audio_setting,
        )

        response = client.text_to_speech(chinese_request)

        # 将hex音频数据转换为bytes
        audio_bytes = binascii.unhexlify(response.data.audio)

        # 保存音频文件
        with open("chinese_output.mp3", "wb") as f:
            f.write(audio_bytes)

        print("✅ 中文音频已保存: chinese_output.mp3")
        print(f"文本长度: {len(chinese_request.text)} 字符")
        if response.extra_info:
            print(f"音频时长: {response.extra_info.audio_length} 毫秒")
            print(f"音频大小: {response.extra_info.audio_size} 字节")
            print(f"计费字符数: {response.extra_info.usage_characters}")

        # eng_tts(client)

        simple_example(client)

    except Exception as e:
        print(f"❌ 错误: {str(e)}")

    finally:
        client.close()


def simple_example(client: MiniMaxSpeech):
    print("\n示例3: 使用简化接口")
    response = client.text_to_speech_simple(
        text="这是一个使用简化接口的示例。",
        voice_id=Voice.CALM_WOMAN,
        model="speech-01-turbo",
        speed=1.2,
        volume=1.0,
        pitch=2,
        format="pcm",
    )
    audio_bytes = binascii.unhexlify(response.data.audio)
    with open("simple_output.wav", "wb") as f:
        f.write(audio_bytes)
    print(f"✅ 简化接口音频已保存: simple_output.wav")
    print(f"文本长度: {len('这是一个使用简化接口的示例。')} 字符")
    if response.extra_info:
        print(f"音频时长: {response.extra_info.audio_length} 毫秒")
        print(f"音频大小: {response.extra_info.audio_size} 字节")
        print(f"计费字符数: {response.extra_info.usage_characters}")
    print("\n🎉 所有示例执行完成！")


def eng_tts(client):
    # 示例2: 英文文本转语音
    print("\n示例2: 英文文本转语音")
    voice_setting = VoiceSetting(voice_id="Grinch", speed=1.0, vol=1.0, pitch=0)
    audio_setting = AudioSetting(sample_rate=32000, bitrate=128000, format="mp3")
    english_request = T2ARequest(
        model="speech-02-hd",
        text="Hello, world! Welcome to MiniMax Speech API.",
        voice_setting=voice_setting,
        audio_setting=audio_setting,
    )
    response = client.text_to_speech(english_request)
    audio_bytes = binascii.unhexlify(response.data.audio)
    with open("english_output.mp3", "wb") as f:
        f.write(audio_bytes)
    print(f"✅ 英文音频已保存: english_output.mp3")
    print(f"文本长度: {len(english_request.text)} 字符")
    if response.extra_info:
        print(f"音频时长: {response.extra_info.audio_length} 毫秒")
        print(f"音频大小: {response.extra_info.audio_size} 字节")
        print(f"计费字符数: {response.extra_info.usage_characters}")


if __name__ == "__main__":
    main()
