"""
MiniMax Speech API 异步使用示例
"""

import asyncio
import os
import binascii
from minimax_speech import AsyncMiniMaxSpeech, T2ARequest, VoiceSetting, AudioSetting


async def main():
    """异步使用示例"""
    
    # 设置API密钥
    api_key = os.getenv("MINIMAX_API_KEY")
    group_id = os.getenv("MINIMAX_GROUP_ID")
    
    if not api_key:
        print("请设置环境变量 MINIMAX_API_KEY")
        return
    
    if not group_id:
        print("请设置环境变量 MINIMAX_GROUP_ID")
        return
    
    # 创建异步客户端
    async with AsyncMiniMaxSpeech(api_key=api_key, group_id=group_id) as client:
        try:
            # 示例1: 单个异步请求
            print("示例1: 单个异步请求")
            
            voice_setting = VoiceSetting(
                voice_id="Wise_Woman",
                speed=1.0,
                vol=1.0,
                pitch=0
            )
            
            audio_setting = AudioSetting(
                sample_rate=32000,
                bitrate=128000,
                format="mp3"
            )
            
            request = T2ARequest(
                model="speech-02-hd",
                text="这是一个异步文本转语音的示例。",
                voice_setting=voice_setting,
                audio_setting=audio_setting
            )
            
            response = await client.text_to_speech(request)
            
            # 将hex音频数据转换为bytes
            audio_bytes = binascii.unhexlify(response.data.audio)
            
            with open("async_single.mp3", "wb") as f:
                f.write(audio_bytes)
            
            print("✅ 异步单次转换完成: async_single.mp3")
            print(f"文本长度: {len(request.text)} 字符")
            if response.extra_info:
                print(f"音频时长: {response.extra_info.audio_length} 毫秒")
                print(f"音频大小: {response.extra_info.audio_size} 字节")
                print(f"计费字符数: {response.extra_info.usage_characters}")
            
            # 示例2: 批量异步请求
            print("\n示例2: 批量异步请求")
            
            requests = []
            texts = [
                "第一段文本。",
                "Second text segment.",
                "Troisième segment de texte.",
                "Четвертый сегмент текста.",
            ]
            
            voice_ids = ["Wise_Woman", "Grinch", "Friendly_Person", "Deep_Voice_Man"]
            
            for text, voice_id in zip(texts, voice_ids):
                voice_setting = VoiceSetting(
                    voice_id=voice_id,
                    speed=1.0,
                    vol=1.0,
                    pitch=0
                )
                
                audio_setting = AudioSetting(
                    sample_rate=32000,
                    bitrate=128000,
                    format="mp3"
                )
                
                request = T2ARequest(
                    model="speech-01-turbo",
                    text=text,
                    voice_setting=voice_setting,
                    audio_setting=audio_setting
                )
                requests.append(request)
            
            responses = await client.batch_text_to_speech(requests, max_concurrent=2)
            
            for i, response in enumerate(responses):
                if isinstance(response, Exception):
                    print(f"❌ 请求 {i+1} 失败: {response}")
                else:
                    filename = f"async_batch_{i+1}.mp3"
                    audio_bytes = binascii.unhexlify(response.data.audio)
                    with open(filename, "wb") as f:
                        f.write(audio_bytes)
                    print(f"✅ 批量转换 {i+1} 完成: {filename}")
                    if response.extra_info:
                        print(f"  音频时长: {response.extra_info.audio_length} 毫秒")
                        print(f"  计费字符数: {response.extra_info.usage_characters}")
            
            # 示例3: 使用简化接口
            print("\n示例3: 使用简化接口")
            
            response = await client.text_to_speech_simple(
                text="这是一个使用简化接口的异步示例。",
                voice_id="Lively_Girl",
                model="speech-01-turbo",
                speed=1.1,
                volume=1.0,
                pitch=1,
                format="mp3"
            )
            
            audio_bytes = binascii.unhexlify(response.data.audio)
            
            with open("async_simple.mp3", "wb") as f:
                f.write(audio_bytes)
            
            print("✅ 异步简化接口完成: async_simple.mp3")
            print(f"文本长度: {len('这是一个使用简化接口的异步示例。')} 字符")
            if response.extra_info:
                print(f"音频时长: {response.extra_info.audio_length} 毫秒")
                print(f"音频大小: {response.extra_info.audio_size} 字节")
                print(f"计费字符数: {response.extra_info.usage_characters}")
            
            print("\n🎉 异步示例执行完成！")
            
        except Exception as e:
            print(f"❌ 错误: {str(e)}")


async def demo_concurrent_processing():
    """演示并发处理"""
    api_key = os.getenv("MINIMAX_API_KEY")
    group_id = os.getenv("MINIMAX_GROUP_ID")
    
    if not api_key or not group_id:
        print("请设置环境变量 MINIMAX_API_KEY 和 MINIMAX_GROUP_ID")
        return
    
    async with AsyncMiniMaxSpeech(api_key=api_key, group_id=group_id) as client:
        # 创建多个并发任务
        tasks = []
        
        texts = [
            "第一个并发任务",
            "Second concurrent task", 
            "Troisième tâche concurrente",
            "Четвертая параллельная задача",
        ]
        
        voice_ids = ["Wise_Woman", "Grinch", "Friendly_Person", "Deep_Voice_Man"]
        
        for i, (text, voice_id) in enumerate(zip(texts, voice_ids)):
            voice_setting = VoiceSetting(
                voice_id=voice_id,
                speed=1.0,
                vol=1.0,
                pitch=0
            )
            
            audio_setting = AudioSetting(
                sample_rate=32000,
                bitrate=128000,
                format="mp3"
            )
            
            request = T2ARequest(
                model="speech-01-turbo",
                text=text,
                voice_setting=voice_setting,
                audio_setting=audio_setting
            )
            
            task = asyncio.create_task(
                client.text_to_speech(request), name=f"task_{i+1}"
            )
            tasks.append(task)
        
        print("开始并发处理...")
        start_time = asyncio.get_event_loop().time()
        
        # 等待所有任务完成
        responses = await asyncio.gather(*tasks, return_exceptions=True)
        
        end_time = asyncio.get_event_loop().time()
        total_time = end_time - start_time
        
        print(f"并发处理完成，总耗时: {total_time:.2f} 秒")
        
        # 保存结果
        for i, response in enumerate(responses):
            if isinstance(response, Exception):
                print(f"❌ 任务 {i+1} 失败: {response}")
            else:
                filename = f"concurrent_{i+1}.mp3"
                audio_bytes = binascii.unhexlify(response.data.audio)
                with open(filename, "wb") as f:
                    f.write(audio_bytes)
                print(f"✅ 并发任务 {i+1} 完成: {filename}")
                if response.extra_info:
                    print(f"  音频时长: {response.extra_info.audio_length} 毫秒")
                    print(f"  计费字符数: {response.extra_info.usage_characters}")


if __name__ == "__main__":
    # 运行基本异步示例
    asyncio.run(main())
    
    # 运行并发处理示例
    print("\n" + "=" * 50)
    print("并发处理示例")
    print("=" * 50)
    asyncio.run(demo_concurrent_processing())
