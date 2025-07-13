# MiniMax Speech

一个基于MiniMax T2A V2 API的Python语音处理包，支持文本转语音(T2A)功能。

## 功能特性

- 🎤 **文本转语音 (T2A)**: 将文本转换为自然语音
- 🎵 **语音列表管理**: 获取系统语音、克隆语音、生成语音等
- 📁 **文件上传**: 支持上传音频文件用于语音克隆
- 🎭 **语音克隆**: 支持基于音频文件创建自定义语音
- 🌍 **多语言支持**: 支持25种语言，包括中文、英文、法文、俄文等
- 🎭 **丰富声音**: 提供17种不同的声音类型
- ⚡ **异步支持**: 提供同步和异步API
- 🔧 **易于使用**: 简洁的API设计
- 📦 **类型安全**: 完整的类型注解支持

## 安装

```bash
pip install minimax-speech
```

## 快速开始

### 基本使用

```python
from minimax_speech import MiniMaxSpeech, T2ARequest, VoiceSetting, AudioSetting
import binascii

# 初始化客户端
client = MiniMaxSpeech(api_key="your_api_key", group_id="your_group_id")

# 创建声音设置
voice_setting = VoiceSetting(
    voice_id="Wise_Woman",
    speed=1.0,
    vol=1.0,
    pitch=0
)

# 创建音频设置
audio_setting = AudioSetting(
    sample_rate=32000,
    bitrate=128000,
    format="mp3"
)

# 创建T2A请求
request = T2ARequest(
    model="speech-02-hd",
    text="你好，世界！",
    voice_setting=voice_setting,
    audio_setting=audio_setting
)

# 生成语音
response = client.text_to_speech(request)

# 将hex音频数据转换为bytes并保存
audio_bytes = binascii.unhexlify(response.data.audio)
with open("output.mp3", "wb") as f:
    f.write(audio_bytes)
```

### 简化接口

```python
# 使用简化接口
response = client.text_to_speech_simple(
    text="Hello, world!",
    voice_id="Grinch",
    model="speech-02-hd",
    speed=1.0,
    volume=1.0,
    pitch=0,
    emotion="happy",  # 可选：happy, sad, angry, fearful, disgusted, surprised, neutral
    format="mp3"
)

audio_bytes = binascii.unhexlify(response.data.audio)
with open("output.mp3", "wb") as f:
    f.write(audio_bytes)
```

### 异步使用

```python
import asyncio
from minimax_speech import AsyncMiniMaxSpeech

async def main():
    async with AsyncMiniMaxSpeech(api_key="your_api_key", group_id="your_group_id") as client:
        request = T2ARequest(
            model="speech-02-hd",
            text="Hello, world!",
            voice_setting=VoiceSetting(voice_id="Wise_Woman"),
            audio_setting=AudioSetting()
        )
        
        response = await client.text_to_speech(request)
        
        audio_bytes = binascii.unhexlify(response.data.audio)
        with open("output.mp3", "wb") as f:
            f.write(audio_bytes)

asyncio.run(main())
```

### 语音列表管理

```python
# 获取所有语音
all_voices = client.get_voice("all")

# 获取系统语音
system_voices = client.get_system_voices()
for voice in system_voices:
    print(f"{voice.voice_name} (ID: {voice.voice_id})")

# 获取克隆语音
cloned_voices = client.get_cloned_voices()
for voice in cloned_voices:
    print(f"克隆语音: {voice.voice_id}, 创建时间: {voice.created_time}")

# 获取特定类型的语音
voice_response = client.get_voice("voice_cloning")
print(f"克隆语音数量: {len(voice_response.voice_cloning)}")

### 文件上传

```python
# 上传音频文件用于语音克隆
file_id = client.file_upload("audio.mp3", purpose="voice_clone")
print(f"文件ID: {file_id}")

# 异步上传文件
async with AsyncMiniMaxSpeech(api_key="your_api_key", group_id="your_group_id") as client:
    file_id = await client.file_upload("audio.mp3", purpose="voice_clone")
    print(f"文件ID: {file_id}")

### 语音克隆

```python
# 上传音频文件
file_id = client.file_upload("audio.mp3", purpose="voice_clone")

# 创建语音克隆
from minimax_speech import VoiceCloneRequest
request = VoiceCloneRequest(
    file_id=file_id,
    voice_id="MyVoice001",  # 必须至少8个字符，包含字母和数字，以字母开头
    need_noise_reduction=True,
    text="你好，这是使用克隆语音生成的测试音频。",
    model="speech-02-hd",
    accuracy=0.8,
    need_volume_normalization=True
)

response = client.voice_clone(request)
print(f"克隆状态: {response.base_resp.status_msg}")

# 使用简化接口
response = client.voice_clone_simple(
    file_id=file_id,
    voice_id="MyVoice001",
    text="这是简化接口的测试。"
)

# 异步语音克隆
async with AsyncMiniMaxSpeech(api_key="your_api_key", group_id="your_group_id") as client:
    response = await client.voice_clone_simple(
        file_id=file_id,
        voice_id="AsyncVoice001",
        text="这是异步语音克隆的测试。"
    )
```

**⚠️ 重要说明：**

1. **`get_voice` 查询限制**: 通过 `get_voice("voice_cloning")` 只能查询到在网页上手动克隆过的音色，无法查询到通过API创建的语音克隆。

2. **语音克隆命名**: 使用 `voice_clone` 创建的音色时，**一定要记住自己设置的 `voice_id`**，因为通过API创建的语音克隆不会在 `get_voice` 查询结果中显示。

3. **删除限制**: `delete_voice` 只能删除通过 `get_voice` 能查询到的音色。通过API创建的语音克隆无法通过 `delete_voice` API删除，需要在网页端手动管理。

## 支持的声音

| 声音ID | 描述 |
|--------|------|
| Wise_Woman | 智慧女性 |
| Friendly_Person | 友好人士 |
| Inspirational_girl | 励志女孩 |
| Deep_Voice_Man | 深沉男声 |
| Calm_Woman | 平静女性 |
| Casual_Guy | 随性男士 |
| Lively_Girl | 活泼女孩 |
| Patient_Man | 耐心男士 |
| Young_Knight | 年轻骑士 |
| Determined_Man | 坚定男士 |
| Lovely_Girl | 可爱女孩 |
| Decent_Boy | 体面男孩 |
| Imposing_Manner | 威严仪态 |
| Elegant_Man | 优雅男士 |
| Abbess | 女修道院长 |
| Sweet_Girl_2 | 甜美女孩2 |
| Exuberant_Girl | 热情女孩 |
| Grinch | 格林奇 |

## 支持的语言

- Chinese (中文)
- Chinese,Yue (粤语)
- English (英语)
- Arabic (阿拉伯语)
- Russian (俄语)
- Spanish (西班牙语)
- French (法语)
- Portuguese (葡萄牙语)
- German (德语)
- Turkish (土耳其语)
- Dutch (荷兰语)
- Ukrainian (乌克兰语)
- Vietnamese (越南语)
- Indonesian (印尼语)
- Japanese (日语)
- Italian (意大利语)
- Korean (韩语)
- Thai (泰语)
- Polish (波兰语)
- Romanian (罗马尼亚语)
- Greek (希腊语)
- Czech (捷克语)
- Finnish (芬兰语)
- Hindi (印地语)
- auto (自动检测)

## 支持的模型

- `speech-02-hd`: 高清语音模型
- `speech-01-turbo`: 快速语音模型
- `speech-01-hd`: 高清语音模型

## 命令行工具

```bash
# 文本转语音
minimax-speech t2a "你好，世界！" --voice-id Wise_Woman --output hello.mp3

# 带情感的文本转语音
minimax-speech t2a "我很开心！" --voice-id Wise_Woman --emotion happy --output happy.mp3
minimax-speech t2a "我很伤心。" --voice-id Wise_Woman --emotion sad --output sad.mp3

# 查看所有语音
minimax-speech voices

# 查看特定类型的语音
minimax-speech voices --type system
minimax-speech voices --type voice_cloning

# 查看支持的语言
minimax-speech languages

# 上传文件
minimax-speech upload audio.mp3 --purpose voice_clone

# 语音克隆
minimax-speech clone file_id_123 MyVoice001 --text "测试文本" --model speech-02-hd
```

## 配置

设置环境变量：

```bash
export MINIMAX_API_KEY="your_api_key"
export MINIMAX_GROUP_ID="your_group_id"
```

或者在代码中直接传入：

```python
client = MiniMaxSpeech(api_key="your_api_key", group_id="your_group_id")
```

## 参数说明

### VoiceSetting 参数

- `voice_id` (str): 声音ID
- `speed` (float): 语速，范围0.5-2.0，默认1.0
- `vol` (float): 音量，范围0-10，默认1.0
- `pitch` (int): 音调，范围-12到12，默认0
- `emotion` (str): 情感，可选值：happy, sad, angry, fearful, disgusted, surprised, neutral

### AudioSetting 参数

- `sample_rate` (int): 采样率，可选值：8000, 16000, 22050, 24000, 32000, 44100，默认32000
- `bitrate` (int): 比特率，可选值：32000, 64000, 128000, 256000，默认128000
- `format` (str): 音频格式，可选值：mp3, pcm, flac，默认mp3
- `channel` (int): 声道数，1或2，默认1

## 错误处理

```python
from minimax_speech import MiniMaxSpeech, MiniMaxAPIError, MiniMaxTimeoutError

try:
    client = MiniMaxSpeech(api_key="your_api_key", group_id="your_group_id")
    response = client.text_to_speech(request)
except MiniMaxAPIError as e:
    print(f"API错误: {e}")
    print(f"状态码: {e.status_code}")
except MiniMaxTimeoutError as e:
    print(f"超时错误: {e}")
except Exception as e:
    print(f"其他错误: {e}")
```

## 开发

```bash
# 克隆仓库
git clone https://github.com/drunkenQCat/minimax-speech.git
cd minimax-speech

# 安装开发依赖
uv sync --all-extras

# 运行测试
pytest

# 代码格式化
black src/
isort src/
```

## 许可证

MIT License

## 贡献

欢迎提交Issue和Pull Request！
