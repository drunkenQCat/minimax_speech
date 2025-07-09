#!/usr/bin/env python3
"""
MiniMax Speech API 语音列表使用示例
"""

import os
import asyncio
from minimax_speech import MiniMaxSpeech, AsyncMiniMaxSpeech


def sync_voice_list_example():
    """同步语音列表示例"""
    print("=== 同步语音列表示例 ===")

    # 创建客户端
    client = MiniMaxSpeech(
        api_key=os.getenv("MINIMAX_API_KEY"), group_id=os.getenv("MINIMAX_GROUP_ID")
    )

    try:
        # 获取所有语音
        print("\n1. 获取所有语音:")
        all_voices = client.get_voice()
        print(
            f"   语音槽位数量: {len(all_voices.voice_slots) if all_voices.voice_slots is not None else 0}"
        )
        print(
            f"   系统语音数量: {len(all_voices.system_voice) if all_voices.system_voice is not None else 0}"
        )
        print(
            f"   克隆语音数量: {len(all_voices.voice_cloning) if all_voices.voice_cloning is not None else 0}"
        )
        print(
            f"   生成语音数量: {len(all_voices.voice_generation) if all_voices.voice_generation is not None else 0}"
        )
        print(
            f"   音乐语音数量: {len(all_voices.music_generation) if all_voices.music_generation is not None else 0}"
        )

        # 获取系统语音
        print("\n2. 获取系统语音:")
        system_voices = client.get_system_voices()
        if system_voices is None:
            print("No system_voice")
        else:
            for i, voice in enumerate(system_voices[:5]):  # 只显示前5个
                print(f"   {i+1}. {voice.voice_name} (ID: {voice.voice_id})")
                print(f"      描述: {', '.join(voice.description)}")

        # 获取克隆语音
        print("\n3. 获取克隆语音:")
        cloned_voices = client.get_cloned_voices()
        if cloned_voices:
            for i, voice in enumerate(cloned_voices):
                print(f"   {i+1}. ID: {voice.voice_id}")
                print(f"      描述: {', '.join(voice.description)}")
                print(f"      创建时间: {voice.created_time}")
        else:
            print("   暂无克隆语音")

        # 获取语音槽位
        print("\n4. 获取语音槽位:")
        voice_slots = client.get_voice_slots()
        if voice_slots:
            for i, slot in enumerate(voice_slots[:3]):  # 只显示前3个
                print(f"   {i+1}. {slot.voice_name} (ID: {slot.voice_id})")
                print(f"      描述: {', '.join(slot.description)}")
        else:
            print("   暂无语音槽位")

        # 获取特定类型的语音
        print("\n5. 获取语音生成类型:")
        generated_voices = client.get_generated_voices()
        if generated_voices:
            for i, voice in enumerate(generated_voices[:3]):  # 只显示前3个
                print(f"   {i+1}. ID: {voice.voice_id}")
                print(f"      描述: {', '.join(voice.description)}")
                print(f"      创建时间: {voice.created_time}")
        else:
            print("   暂无生成语音")

        # 获取音乐语音
        print("\n6. 获取音乐语音:")
        music_voices = client.get_music_voices()
        if music_voices:
            for i, voice in enumerate(music_voices[:3]):  # 只显示前3个
                print(f"   {i+1}. 语音ID: {voice.voice_id}")
                print(f"      乐器ID: {voice.instrumental_id}")
                print(f"      创建时间: {voice.created_time}")
        else:
            print("   暂无音乐语音")

    except Exception as e:
        print(f"❌ 错误: {e}")
    finally:
        client.close()


async def async_voice_list_example():
    """异步语音列表示例"""
    print("\n=== 异步语音列表示例 ===")

    async with AsyncMiniMaxSpeech(
        api_key=os.getenv("MINIMAX_API_KEY"), group_id=os.getenv("MINIMAX_GROUP_ID")
    ) as client:
        try:
            # 获取所有语音
            print("\n1. 获取所有语音:")
            all_voices = await client.get_voice("all")
            print(
                f"   语音槽位数量: {len(all_voices.voice_slots) if all_voices.voice_slots is not None else 0}"
            )
            print(
                f"   系统语音数量: {len(all_voices.system_voice)if all_voices.system_voice is not None else 0}"
            )
            print(
                f"   克隆语音数量: {len(all_voices.voice_cloning)if all_voices.voice_cloning is not None else 0}"
            )
            print(
                f"   生成语音数量: {len(all_voices.voice_generation)if all_voices.voice_generation is not None else 0}"
            )
            print(
                f"   音乐语音数量: {len(all_voices.music_generation) if all_voices.music_generation is not None else 0}"
            )

            # 获取系统语音
            print("\n2. 获取系统语音:")
            system_voices = await client.get_system_voices()
            if system_voices is None:
                print("No System Voices")
            else:
                for i, voice in enumerate(system_voices[:5]):  # 只显示前5个
                    print(f"   {i+1}. {voice.voice_name} (ID: {voice.voice_id})")
                    print(f"      描述: {', '.join(voice.description)}")

            # 获取克隆语音
            print("\n3. 获取克隆语音:")
            cloned_voices = await client.get_cloned_voices()
            if cloned_voices:
                for i, voice in enumerate(cloned_voices[:3]):  # 只显示前3个
                    print(f"   {i+1}. ID: {voice.voice_id}")
                    print(f"      描述: {', '.join(voice.description)}")
                    print(f"      创建时间: {voice.created_time}")
            else:
                print("   暂无克隆语音")

        except Exception as e:
            print(f"❌ 错误: {e}")


def voice_analysis_example():
    """语音分析示例"""
    print("\n=== 语音分析示例 ===")

    client = MiniMaxSpeech(
        api_key=os.getenv("MINIMAX_API_KEY"), group_id=os.getenv("MINIMAX_GROUP_ID")
    )

    try:
        # 获取所有语音
        all_voices = client.get_voice("all")

        # 分析系统语音
        print("\n系统语音分析:")
        system_voices = all_voices.system_voice
        print(f"   总数: {len(system_voices) if system_voices is not None else 0}")

        # 按描述分类
        voice_categories = {}
        if system_voices is None:
            print("No System Voice")
        else:
            for voice in system_voices:
                for desc in voice.description:
                    if desc not in voice_categories:
                        voice_categories[desc] = []
                    voice_categories[desc].append(voice.voice_name)

        print("   按类型分类:")
        for category, voices in voice_categories.items():
            print(f"     {category}: {len(voices)} 个语音")
            if len(voices) <= 5:
                print(f"       示例: {', '.join(voices)}")
            else:
                print(f"       示例: {', '.join(voices[:5])}...")

        # 分析克隆语音
        print("\n克隆语音分析:")
        cloned_voices = all_voices.voice_cloning
        if cloned_voices is None:
            print("No cloned_voices")
        else:
            print(f"   总数: {len(cloned_voices)}")

        if cloned_voices:
            # 按创建时间分析
            from collections import Counter

            creation_months = [
                voice.created_time[:7] for voice in cloned_voices
            ]  # 取年月
            month_counts = Counter(creation_months)

            print("   按创建时间分布:")
            for month, count in sorted(month_counts.items()):
                print(f"     {month}: {count} 个语音")

        # 分析语音槽位
        print("\n语音槽位分析:")
        voice_slots = all_voices.voice_slots
        print(f"   总数: {len(voice_slots) if voice_slots is not None else 0}")

        if voice_slots:
            # 按名称分析
            name_patterns = {}
            for slot in voice_slots:
                name = slot.voice_name.lower()
                if "woman" in name:
                    name_patterns["woman"] = name_patterns.get("woman", 0) + 1
                elif "man" in name:
                    name_patterns["man"] = name_patterns.get("man", 0) + 1
                elif "child" in name or "kid" in name:
                    name_patterns["child"] = name_patterns.get("child", 0) + 1
                else:
                    name_patterns["other"] = name_patterns.get("other", 0) + 1

            print("   按名称模式分类:")
            for pattern, count in name_patterns.items():
                print(f"     {pattern}: {count} 个语音")

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
    sync_voice_list_example()

    # 运行异步示例
    # asyncio.run(async_voice_list_example())

    # 运行分析示例
    # voice_analysis_example()

    print("\n✅ 所有示例运行完成！")

