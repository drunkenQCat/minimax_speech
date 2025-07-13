"""
MiniMax Speech API 异步客户端
"""

import json
import asyncio
from typing import Optional, List
import aiohttp

from .config import APIConfig
from .tts_models import (
    T2ARequest,
    T2AResponse,
)
from .common_models import (
    ValidEmotions,
    ValidSr,
    ValidBitRate,
    ValidAudioFormat,
    ValidModels,
)
from .exceptions import MiniMaxAPIError, MiniMaxTimeoutError
from .voice_query_models import VoiceListResponse, VoiceSlot, VoiceType
from .file_upload_models import FileUploadResponse
from .voice_clone_models import VoiceCloneRequest, VoiceCloneResponse


class AsyncMiniMaxSpeech:
    """MiniMax Speech API 异步客户端"""

    def __init__(
        self,
        api_key: Optional[str] = None,
        group_id: Optional[str] = None,
        base_url: Optional[str] = None,
        timeout: Optional[int] = None,
        max_retries: Optional[int] = None,
    ):
        self.config = APIConfig(
            api_key=api_key,
            group_id=group_id,
            base_url=base_url,
            timeout=timeout,
            max_retries=max_retries,
        )
        self.session: Optional[aiohttp.ClientSession] = None

    async def __aenter__(self):
        """异步上下文管理器入口"""
        await self._ensure_session()
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """异步上下文管理器出口"""
        await self.close()

    async def _ensure_session(self):
        """确保session已创建"""
        if self.session is None or self.session.closed:
            timeout = aiohttp.ClientTimeout(total=self.config.timeout)
            self.session = aiohttp.ClientSession(
                timeout=timeout, headers=self.config.get_headers()
            )

    async def get_voice(self, voice_type: VoiceType = "all") -> VoiceListResponse:
        """
        获取语音列表（异步）

        Args:
            voice_type: 语音类型，可选值：
                - "system": 系统语音
                - "voice_cloning": 克隆语音
                - "voice_generation": 语音生成
                - "music_generation": 音乐生成
                - "all": 所有语音（默认）

        Returns:
            VoiceListResponse: 语音列表响应对象

        Raises:
            MiniMaxAPIError: API错误
            MiniMaxTimeoutError: 超时错误
        """
        await self._ensure_session()

        if self.session is None:
            raise MiniMaxAPIError("Sesson创建失败")
        # 使用正确的语音列表API端点
        url = self.config.voice_list_url

        # 构建请求参数
        params = {"voice_type": voice_type}

        try:
            async with self.session.post(url, params=params) as response:
                # 检查HTTP状态码
                if response.status != 200:
                    text = await response.text()
                    raise MiniMaxAPIError(
                        f"HTTP {response.status}: {text}",
                        status_code=response.status,
                        response_data={"text": text},
                    )

                # 解析响应
                data = await response.json()
                voice_response = VoiceListResponse(**data)

                # 检查业务状态码
                if not voice_response.base_resp.is_success:
                    raise MiniMaxAPIError(
                        f"API Error: {voice_response.base_resp.error_type}",
                        status_code=voice_response.base_resp.status_code,
                        response_data=data,
                    )

                return voice_response

        except asyncio.TimeoutError:
            raise MiniMaxTimeoutError("Request timed out")
        except aiohttp.ClientError as e:
            raise MiniMaxAPIError(f"Request failed: {str(e)}")
        except json.JSONDecodeError as e:
            raise MiniMaxAPIError(f"Invalid JSON response: {str(e)}")

    async def get_voice_slots(self) -> list[VoiceSlot] | None:
        """
        获取语音槽位列表（异步）

        Returns:
            list: 语音槽位列表
        """
        response = await self.get_voice("all")
        return response.voice_slots

    async def get_system_voices(self) -> list | None:
        """
        获取系统语音列表（异步）

        Returns:
            list: 系统语音列表
        """
        response = await self.get_voice("system")
        return response.system_voice

    async def get_cloned_voices(self) -> list | None:
        """
        获取克隆语音列表（异步）

        Returns:
            list: 克隆语音列表
        """
        response = await self.get_voice("voice_cloning")
        return response.voice_cloning

    async def get_generated_voices(self) -> list | None:
        """
        获取生成的语音列表（异步）

        Returns:
            list: 生成的语音列表
        """
        response = await self.get_voice("voice_generation")
        return response.voice_generation

    async def get_music_voices(self) -> list | None:
        """
        获取音乐生成语音列表（异步）

        Returns:
            list: 音乐生成语音列表
        """
        response = await self.get_voice("music_generation")
        return response.music_generation

    async def file_upload(
        self, input_file_path: str, purpose: str = "voice_clone"
    ) -> int:
        """
        上传文件（异步）

        Args:
            file_path: 文件路径
            purpose: 文件用途，默认为"voice_clone"

        Returns:
            str: 文件ID

        Raises:
            MiniMaxAPIError: API错误
            MiniMaxTimeoutError: 超时错误
            FileNotFoundError: 文件不存在
        """
        await self._ensure_session()
        if self.session is None:
            raise MiniMaxAPIError("Sesson创建失败")

        from pathlib import Path

        # 检查文件是否存在
        file_path = Path(input_file_path)
        if not file_path.exists():
            raise FileNotFoundError(f"文件不存在: {file_path}")

        # 构建上传URL
        url = f"{self.config.base_url}/files/upload?GroupId={self.config.group_id}"

        # 准备请求数据
        data = aiohttp.FormData()
        data.add_field("purpose", purpose)

        # 准备文件
        with open(file_path, "rb") as f:
            data.add_field(
                "file",
                f,
                filename=file_path.name,
                content_type="application/octet-stream",
            )

            try:
                async with self.session.post(url, data=data) as response:
                    # 检查HTTP状态码
                    if response.status != 200:
                        text = await response.text()
                        raise MiniMaxAPIError(
                            f"HTTP {response.status}: {text}",
                            status_code=response.status,
                            response_data={"text": text},
                        )

                    # 解析响应
                    data = await response.json()
                    upload_response = FileUploadResponse(**data)

                    # 检查业务状态码
                    if not upload_response.base_resp.is_success:
                        raise MiniMaxAPIError(
                            f"API Error: {upload_response.base_resp.error_type}",
                            status_code=upload_response.base_resp.status_code,
                            response_data=data,
                        )

                    return upload_response.file.file_id

            except asyncio.TimeoutError:
                raise MiniMaxTimeoutError("Request timed out")
            except aiohttp.ClientError as e:
                raise MiniMaxAPIError(f"Request failed: {str(e)}")
            except json.JSONDecodeError as e:
                raise MiniMaxAPIError(f"Invalid JSON response: {str(e)}")

    async def voice_clone(self, request: VoiceCloneRequest) -> VoiceCloneResponse:
        """
        语音克隆（异步）

        Args:
            request: 语音克隆请求对象

        Returns:
            VoiceCloneResponse: 语音克隆响应对象

        Raises:
            MiniMaxAPIError: API错误
            MiniMaxTimeoutError: 超时错误
        """
        await self._ensure_session()
        if self.session is None:
            raise MiniMaxAPIError("Session创建失败")

        # 验证请求
        self._validate_voice_clone_request(request)

        # 发送语音克隆请求
        return await self._submit_voice_clone_request(request)

    def _validate_voice_clone_request(self, request: VoiceCloneRequest) -> None:
        """验证语音克隆请求"""
        # 验证voice_id格式
        if len(request.voice_id) < 8:
            raise ValueError("voice_id must be at least 8 characters long")

        if not request.voice_id[0].isalpha():
            raise ValueError("voice_id must start with a letter")

        has_letter = any(c.isalpha() for c in request.voice_id)
        has_digit = any(c.isdigit() for c in request.voice_id)

        if not (has_letter and has_digit):
            raise ValueError("voice_id must contain both letters and numbers")

        # 验证text长度
        if request.text and len(request.text) > 2000:
            raise ValueError("text too long, maximum 2000 characters allowed")

        # 验证accuracy范围
        if request.accuracy is not None and not (0 <= request.accuracy <= 1):
            raise ValueError("accuracy must be between 0 and 1")

        # 验证model
        if request.model:
            valid_models = [
                "speech-02-hd",
                "speech-02-turbo",
                "speech-01-hd",
                "speech-01-turbo",
            ]
            if request.model not in valid_models:
                raise ValueError(f"Invalid model: {request.model}")

    async def _submit_voice_clone_request(
        self, request: VoiceCloneRequest
    ) -> VoiceCloneResponse:
        """提交语音克隆请求（异步）"""
        if self.session is None:
            raise MiniMaxAPIError("Session Not Ready!")
        url = self.config.voice_clone_url

        # 构建请求数据
        payload = request.model_dump(exclude_none=True)

        try:
            async with self.session.post(url, json=payload) as response:
                # 检查HTTP状态码
                if response.status != 200:
                    text = await response.text()
                    raise MiniMaxAPIError(
                        f"HTTP {response.status}: {text}",
                        status_code=response.status,
                        response_data={"text": text},
                    )

                # 解析响应
                data = await response.json()
                voice_clone_response = VoiceCloneResponse(**data)

                # 检查业务状态码
                if not voice_clone_response.base_resp.is_success:
                    raise MiniMaxAPIError(
                        f"API Error: {voice_clone_response.base_resp.error_type}",
                        status_code=voice_clone_response.base_resp.status_code,
                        response_data=data,
                    )

                return voice_clone_response

        except asyncio.TimeoutError:
            raise MiniMaxTimeoutError("Request timed out")
        except aiohttp.ClientError as e:
            raise MiniMaxAPIError(f"Request failed: {str(e)}")
        except json.JSONDecodeError as e:
            raise MiniMaxAPIError(f"Invalid JSON response: {str(e)}")

    async def voice_clone_simple(
        self,
        file_id: int,
        voice_id: str,
        need_noise_reduction: bool = False,
        text: Optional[str] = None,
        model: Optional[ValidModels] = None,
        accuracy: Optional[float] = 0.7,
        need_volume_normalization: bool = False,
    ) -> VoiceCloneResponse:
        """
        简化的语音克隆接口（异步）

        Args:
            file_id: 要克隆的文件ID
            voice_id: 自定义用户定义的ID
            need_noise_reduction: 是否启用降噪
            text: 预览文本
            model: TTS模型
            accuracy: 文本验证精度阈值
            need_volume_normalization: 是否启用音量标准化

        Returns:
            VoiceCloneResponse: 语音克隆响应对象
        """
        request = VoiceCloneRequest(
            file_id=file_id,
            voice_id=voice_id,
            need_noise_reduction=need_noise_reduction,
            text=text,
            model=model,
            accuracy=accuracy,
            need_volume_normalization=need_volume_normalization,
        )

        return await self.voice_clone(request)

    async def text_to_speech(self, request: T2ARequest) -> T2AResponse:
        """
        文本转语音（异步）

        Args:
            request: T2A请求对象

        Returns:
            T2AResponse: 语音响应对象

        Raises:
            MiniMaxAPIError: API错误
            MiniMaxTimeoutError: 超时错误
        """
        await self._ensure_session()

        # 验证请求
        self._validate_t2a_request(request)

        # 发送T2A请求
        return await self._submit_t2a_request(request)

    def _validate_t2a_request(self, request: T2ARequest) -> None:
        """验证T2A请求"""
        if not request.text.strip():
            raise ValueError("Text cannot be empty")

        if len(request.text) > 5000:
            raise ValueError("Text too long, maximum 5000 characters allowed")

        # 验证模型
        valid_models = ["speech-02-hd", "speech-01-turbo", "speech-01-hd"]
        if request.model not in valid_models:
            raise ValueError(f"Invalid model: {request.model}")

    async def _submit_t2a_request(self, request: T2ARequest) -> T2AResponse:
        """提交T2A请求（异步）"""
        url = self.config.t2a_url
        if self.session is None:
            raise MiniMaxAPIError("Sesson创建失败")

        # 构建请求数据
        payload = request.model_dump(exclude_none=True)

        try:
            async with self.session.post(url, json=payload) as response:
                # 检查HTTP状态码
                if response.status != 200:
                    text = await response.text()
                    raise MiniMaxAPIError(
                        f"HTTP {response.status}: {text}",
                        status_code=response.status,
                        response_data={"text": text},
                    )

                # 解析响应
                data = await response.json()
                t2a_response = T2AResponse(**data)

                # 检查业务状态码
                if not t2a_response.base_resp.is_success:
                    raise MiniMaxAPIError(
                        f"API Error: {t2a_response.base_resp.error_type}",
                        status_code=t2a_response.base_resp.status_code,
                        response_data=data,
                    )

                return t2a_response

        except asyncio.TimeoutError:
            raise MiniMaxTimeoutError("Request timed out")
        except aiohttp.ClientError as e:
            raise MiniMaxAPIError(f"Request failed: {str(e)}")
        except json.JSONDecodeError as e:
            raise MiniMaxAPIError(f"Invalid JSON response: {str(e)}")

    async def text_to_speech_simple(
        self,
        text: str,
        voice_id: str = "Wise_Woman",
        model: ValidModels = "speech-02-hd",
        speed: float = 1.0,
        volume: float = 1.0,
        pitch: int = 0,
        emotion: Optional[ValidEmotions] = None,
        format: ValidAudioFormat = "mp3",
        sample_rate: ValidSr = 32000,
        bitrate: ValidBitRate = 128000,
    ) -> T2AResponse:
        """
        简化的文本转语音接口（异步）

        Args:
            text: 要转换的文本
            voice_id: 声音ID
            model: 模型名称
            speed: 语速 (0.5-2.0)
            volume: 音量 (0-10)
            pitch: 音调 (-12到12)
            emotion: 情感 (happy, sad, angry, fearful, disgusted, surprised, neutral)
            format: 音频格式 (mp3, pcm, flac)
            sample_rate: 采样率
            bitrate: 比特率

        Returns:
            T2AResponse: 语音响应对象
        """
        from .tts_models import VoiceSetting, AudioSetting, T2ARequest

        voice_setting = VoiceSetting(
            voice_id=voice_id, speed=speed, vol=volume, pitch=pitch, emotion=emotion
        )

        audio_setting = AudioSetting(
            sample_rate=sample_rate, bitrate=bitrate, format=format
        )

        request = T2ARequest(
            model=model,
            text=text,
            voice_setting=voice_setting,
            audio_setting=audio_setting,
        )

        return await self.text_to_speech(request)

    async def batch_text_to_speech(
        self, requests: List[T2ARequest], max_concurrent: int = 5
    ) -> List[T2AResponse | BaseException]:
        """
        批量文本转语音

        Args:
            requests: T2A请求列表
            max_concurrent: 最大并发数

        Returns:
            List[T2AResponse]: 响应列表
        """
        semaphore = asyncio.Semaphore(max_concurrent)

        async def process_single_request(req: T2ARequest) -> T2AResponse:
            async with semaphore:
                return await self.text_to_speech(req)

        tasks = [process_single_request(req) for req in requests]
        return await asyncio.gather(*tasks, return_exceptions=True)

    async def close(self):
        """关闭客户端"""
        if self.session and not self.session.closed:
            await self.session.close()
