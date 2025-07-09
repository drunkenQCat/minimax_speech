"""
MiniMax Speech CLI 工具
"""

import argparse
import sys
import os
from pathlib import Path
from typing import Optional

from .client import MiniMaxSpeech
from .tts_models import T2ARequest, Language, Voice, VoiceSetting, AudioSetting
from .config import VoiceConfig, LanguageConfig


def main():
    """主函数"""
    parser = create_parser()
    args = parser.parse_args()
    
    if args.command == "t2a":
        handle_t2a_command(args)
    elif args.command == "voices":
        handle_voices_command(args)
    elif args.command == "languages":
        handle_languages_command()
    elif args.command == "upload":
        handle_upload_command(args)
    elif args.command == "clone":
        handle_clone_command(args)
    else:
        parser.print_help()
        sys.exit(1)


def create_parser() -> argparse.ArgumentParser:
    """创建命令行解析器"""
    parser = argparse.ArgumentParser(
        prog="minimax-speech",
        description="MiniMax Speech API 命令行工具",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
示例:
  minimax-speech t2a "你好，世界！" --voice-id Wise_Woman --output hello.mp3
  minimax-speech t2a "Hello, world!" --voice-id Grinch --model speech-02-hd --format mp3
  minimax-speech voices
  minimax-speech voices --type system
  minimax-speech languages
  minimax-speech upload audio.mp3 --purpose voice_clone
  minimax-speech clone file_id_123 MyVoice001 --text "测试文本" --model speech-02-hd
        """
    )
    
    subparsers = parser.add_subparsers(dest="command", help="可用命令")
    
    # T2A 命令
    t2a_parser = subparsers.add_parser("t2a", help="文本转语音")
    t2a_parser.add_argument("text", help="要转换的文本")
    t2a_parser.add_argument("--voice-id", required=True, help="声音ID")
    t2a_parser.add_argument("--model", default="speech-02-hd", 
                           choices=["speech-02-hd", "speech-01-turbo", "speech-01-hd"],
                           help="模型名称")
    t2a_parser.add_argument("--output", "-o", required=True, help="输出文件路径")
    t2a_parser.add_argument("--speed", "-s", type=float, default=1.0, help="语速 (0.5-2.0)")
    t2a_parser.add_argument("--volume", type=float, default=1.0, help="音量 (0-10)")
    t2a_parser.add_argument("--pitch", type=int, default=0, help="音调 (-12到12)")
    t2a_parser.add_argument("--format", "-f", choices=["mp3", "pcm", "flac"], default="mp3", help="输出格式")
    t2a_parser.add_argument("--sample-rate", type=int, default=32000, help="采样率")
    t2a_parser.add_argument("--bitrate", type=int, default=128000, help="比特率")
    t2a_parser.add_argument("--api-key", help="API密钥")
    t2a_parser.add_argument("--group-id", help="Group ID")
    
    # 声音列表命令
    voices_parser = subparsers.add_parser("voices", help="显示可用的声音")
    voices_parser.add_argument("--type", choices=["all", "system", "voice_cloning", "voice_generation", "music_generation"], 
                              default="all", help="语音类型")
    voices_parser.add_argument("--api-key", help="API密钥")
    voices_parser.add_argument("--group-id", help="Group ID")
    
    # 语言列表命令
    languages_parser = subparsers.add_parser("languages", help="显示支持的语言")
    
    # 文件上传命令
    upload_parser = subparsers.add_parser("upload", help="上传文件")
    upload_parser.add_argument("file", help="要上传的文件路径")
    upload_parser.add_argument("--purpose", default="voice_clone", help="文件用途")
    upload_parser.add_argument("--api-key", help="API密钥")
    upload_parser.add_argument("--group-id", help="Group ID")
    
    # 语音克隆命令
    clone_parser = subparsers.add_parser("clone", help="语音克隆")
    clone_parser.add_argument("file_id", help="要克隆的文件ID")
    clone_parser.add_argument("voice_id", help="自定义语音ID（至少8个字符，包含字母和数字，以字母开头）")
    clone_parser.add_argument("--text", help="预览文本（限制2000字符）")
    clone_parser.add_argument("--model", choices=["speech-02-hd", "speech-02-turbo", "speech-01-hd", "speech-01-turbo"], 
                             default="speech-02-hd", help="TTS模型")
    clone_parser.add_argument("--accuracy", type=float, default=0.7, help="文本验证精度阈值 (0-1)")
    clone_parser.add_argument("--noise-reduction", action="store_true", help="启用降噪")
    clone_parser.add_argument("--volume-normalization", action="store_true", help="启用音量标准化")
    clone_parser.add_argument("--api-key", help="API密钥")
    clone_parser.add_argument("--group-id", help="Group ID")
    
    return parser


def handle_t2a_command(args):
    """处理T2A命令"""
    try:
        # 验证参数
        validate_t2a_args(args)
        
        # 创建客户端
        client = MiniMaxSpeech(api_key=args.api_key, group_id=args.group_id)
        
        # 创建请求
        request = create_t2a_request(args)
        
        print(f"正在转换文本: {args.text}")
        print(f"使用声音: {args.voice_id}")
        print(f"模型: {args.model}")
        print(f"输出格式: {args.format}")
        
        # 执行转换
        response = client.text_to_speech(request)
        
        # 保存文件
        output_path = Path(args.output)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        
        # 将hex音频数据转换为bytes
        import binascii
        audio_bytes = binascii.unhexlify(response.data.audio)
        
        with open(output_path, "wb") as f:
            f.write(audio_bytes)
        
        print(f"✅ 转换完成！音频已保存到: {output_path}")
        print(f"文本长度: {len(args.text)} 字符")
        if response.extra_info:
            print(f"音频时长: {response.extra_info.audio_length} 毫秒")
            print(f"音频大小: {response.extra_info.audio_size} 字节")
            print(f"计费字符数: {response.extra_info.usage_characters}")
        
    except Exception as e:
        print(f"❌ 错误: {str(e)}", file=sys.stderr)
        sys.exit(1)
    finally:
        if 'client' in locals():
            client.close()


def create_t2a_request(args) -> T2ARequest:
    """创建T2A请求"""
    voice_setting = VoiceSetting(
        voice_id=args.voice_id,
        speed=args.speed,
        vol=args.volume,
        pitch=args.pitch
    )
    
    audio_setting = AudioSetting(
        sample_rate=args.sample_rate,
        bitrate=args.bitrate,
        format=args.format
    )
    
    return T2ARequest(
        model=args.model,
        text=args.text,
        voice_setting=voice_setting,
        audio_setting=audio_setting
    )


def handle_voices_command(args):
    """处理声音列表命令"""
    try:
        # 创建客户端
        client = MiniMaxSpeech(api_key=args.api_key, group_id=args.group_id)
        
        print(f"获取 {args.type} 类型的语音列表...")
        
        # 获取语音列表
        voice_response = client.get_voice(args.type)
        
        if args.type == "all" or args.type == "system":
            print("\n系统语音:")
            print("-" * 50)
            for i, voice in enumerate(voice_response.system_voice, 1):
                print(f"{i:2d}. {voice.voice_name:<20} (ID: {voice.voice_id})")
                print(f"     描述: {', '.join(voice.description)}")
                print()
        
        if args.type == "all" or args.type == "voice_cloning":
            print("\n克隆语音:")
            print("-" * 50)
            if voice_response.voice_cloning:
                for i, voice in enumerate(voice_response.voice_cloning, 1):
                    print(f"{i:2d}. ID: {voice.voice_id}")
                    print(f"     描述: {', '.join(voice.description)}")
                    print(f"     创建时间: {voice.created_time}")
                    print()
            else:
                print("暂无克隆语音")
        
        if args.type == "all" or args.type == "voice_generation":
            print("\n生成语音:")
            print("-" * 50)
            if voice_response.voice_generation:
                for i, voice in enumerate(voice_response.voice_generation, 1):
                    print(f"{i:2d}. ID: {voice.voice_id}")
                    print(f"     描述: {', '.join(voice.description)}")
                    print(f"     创建时间: {voice.created_time}")
                    print()
            else:
                print("暂无生成语音")
        
        if args.type == "all" or args.type == "music_generation":
            print("\n音乐语音:")
            print("-" * 50)
            if voice_response.music_generation:
                for i, voice in enumerate(voice_response.music_generation, 1):
                    print(f"{i:2d}. 语音ID: {voice.voice_id}")
                    print(f"     乐器ID: {voice.instrumental_id}")
                    print(f"     创建时间: {voice.created_time}")
                    print()
            else:
                print("暂无音乐语音")
        
        if args.type == "all":
            print("\n语音槽位:")
            print("-" * 50)
            if voice_response.voice_slots:
                for i, slot in enumerate(voice_response.voice_slots, 1):
                    print(f"{i:2d}. {slot.voice_name:<20} (ID: {slot.voice_id})")
                    print(f"     描述: {', '.join(slot.description)}")
                    print()
            else:
                print("暂无语音槽位")
        
        # 统计信息
        print("\n统计信息:")
        print("-" * 30)
        print(f"系统语音: {len(voice_response.system_voice)} 个")
        print(f"克隆语音: {len(voice_response.voice_cloning)} 个")
        print(f"生成语音: {len(voice_response.voice_generation)} 个")
        print(f"音乐语音: {len(voice_response.music_generation)} 个")
        print(f"语音槽位: {len(voice_response.voice_slots)} 个")
        
    except Exception as e:
        print(f"❌ 错误: {str(e)}", file=sys.stderr)
        sys.exit(1)
    finally:
        if 'client' in locals():
            client.close()


def handle_languages_command():
    """处理语言列表命令"""
    print("支持的语言:")
    print("-" * 30)
    
    languages = [
        ("Chinese", "中文"),
        ("Chinese,Yue", "粤语"),
        ("English", "英语"),
        ("Arabic", "阿拉伯语"),
        ("Russian", "俄语"),
        ("Spanish", "西班牙语"),
        ("French", "法语"),
        ("Portuguese", "葡萄牙语"),
        ("German", "德语"),
        ("Turkish", "土耳其语"),
        ("Dutch", "荷兰语"),
        ("Ukrainian", "乌克兰语"),
        ("Vietnamese", "越南语"),
        ("Indonesian", "印尼语"),
        ("Japanese", "日语"),
        ("Italian", "意大利语"),
        ("Korean", "韩语"),
        ("Thai", "泰语"),
        ("Polish", "波兰语"),
        ("Romanian", "罗马尼亚语"),
        ("Greek", "希腊语"),
        ("Czech", "捷克语"),
        ("Finnish", "芬兰语"),
        ("Hindi", "印地语"),
        ("auto", "自动检测")
    ]
    
    for lang_code, lang_name in languages:
        print(f"{lang_code:<15} - {lang_name}")
    
    print(f"\n总计: {len(languages)} 种语言")


def handle_upload_command(args):
    """处理文件上传命令"""
    try:
        # 验证文件是否存在
        if not os.path.exists(args.file):
            print(f"❌ 文件不存在: {args.file}", file=sys.stderr)
            sys.exit(1)
        
        # 创建客户端
        client = MiniMaxSpeech(api_key=args.api_key, group_id=args.group_id)
        
        print(f"正在上传文件: {args.file}")
        print(f"文件用途: {args.purpose}")
        
        # 获取文件信息
        file_size = os.path.getsize(args.file)
        print(f"文件大小: {file_size} 字节")
        
        # 上传文件
        file_id = client.file_upload(args.file, purpose=args.purpose)
        
        print(f"✅ 文件上传成功！")
        print(f"文件ID: {file_id}")
        
    except Exception as e:
        print(f"❌ 错误: {str(e)}", file=sys.stderr)
        sys.exit(1)
    finally:
        if 'client' in locals():
            client.close()


def handle_clone_command(args):
    """处理语音克隆命令"""
    try:
        # 创建客户端
        client = MiniMaxSpeech(api_key=args.api_key, group_id=args.group_id)
        
        print(f"正在克隆语音...")
        print(f"文件ID: {args.file_id}")
        print(f"语音ID: {args.voice_id}")
        
        if args.text:
            print(f"预览文本: {args.text}")
        print(f"模型: {args.model}")
        print(f"精度: {args.accuracy}")
        print(f"降噪: {args.noise_reduction}")
        print(f"音量标准化: {args.volume_normalization}")
        
        # 执行语音克隆
        response = client.voice_clone_simple(
            file_id=args.file_id,
            voice_id=args.voice_id,
            text=args.text,
            model=args.model,
            accuracy=args.accuracy,
            need_noise_reduction=args.noise_reduction,
            need_volume_normalization=args.volume_normalization
        )
        
        print(f"✅ 语音克隆成功！")
        print(f"输入敏感: {response.input_sensitive}")
        print(f"状态码: {response.base_resp.status_code}")
        print(f"状态消息: {response.base_resp.status_msg}")
        
    except Exception as e:
        print(f"❌ 错误: {str(e)}", file=sys.stderr)
        sys.exit(1)
    finally:
        if 'client' in locals():
            client.close()


def validate_t2a_args(args):
    """验证T2A参数"""
    # 检查语速范围
    if not 0.5 <= args.speed <= 2.0:
        print("❌ 语速必须在 0.5 到 2.0 之间")
        sys.exit(1)
    
    # 检查音量范围
    if not 0.0 <= args.volume <= 10.0:
        print("❌ 音量必须在 0.0 到 10.0 之间")
        sys.exit(1)
    
    # 检查音调范围
    if not -12 <= args.pitch <= 12:
        print("❌ 音调必须在 -12 到 12 之间")
        sys.exit(1)
    
    # 检查采样率
    valid_sample_rates = [8000, 16000, 22050, 24000, 32000, 44100]
    if args.sample_rate not in valid_sample_rates:
        print(f"❌ 采样率必须是以下之一: {valid_sample_rates}")
        sys.exit(1)
    
    # 检查比特率
    valid_bitrates = [32000, 64000, 128000, 256000]
    if args.bitrate not in valid_bitrates:
        print(f"❌ 比特率必须是以下之一: {valid_bitrates}")
        sys.exit(1)


if __name__ == "__main__":
    main() 
