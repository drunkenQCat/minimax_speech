import struct
import os


def pcm_to_wav(
    pcm_path: str, wav_path: str, channels: int, sample_rate: int, bits_per_sample: int
) -> None:
    """将裸PCM文件封装成WAV文件

    参数:
        pcm_path: PCM原始文件路径
        wav_path: 输出的WAV文件路径
        channels: 声道数量 (1=单声道, 2=立体声)
        sample_rate: 采样率 (如 44100, 48000)
        bits_per_sample: 每个采样的位深度 (如 16, 24)
    """

    # 读取PCM原始数据
    with open(pcm_path, "rb") as pcm_file:
        pcm_data: bytes = pcm_file.read()

    data_size: int = len(pcm_data)
    byte_rate: int = sample_rate * channels * bits_per_sample // 8
    block_align: int = channels * bits_per_sample // 8
    fmt_chunk_size: int = 16
    audio_format: int = 1  # PCM = 1

    # 构建RIFF头
    wav_header: bytes = b"RIFF"
    wav_header += struct.pack("<I", 36 + data_size)  # RIFF块大小
    wav_header += b"WAVE"

    # fmt 子块
    wav_header += b"fmt "
    wav_header += struct.pack("<I", fmt_chunk_size)  # 子块大小 16
    wav_header += struct.pack("<H", audio_format)  # 音频格式 1 = PCM
    wav_header += struct.pack("<H", channels)
    wav_header += struct.pack("<I", sample_rate)
    wav_header += struct.pack("<I", byte_rate)
    wav_header += struct.pack("<H", block_align)
    wav_header += struct.pack("<H", bits_per_sample)

    # data 子块
    wav_header += b"data"
    wav_header += struct.pack("<I", data_size)

    # 写入WAV文件
    with open(wav_path, "wb") as wav_file:
        wav_file.write(wav_header)
        wav_file.write(pcm_data)

    print(f"WAV文件已生成：{wav_path}")


# 使用示例
if __name__ == "__main__":
    pcm_to_wav(
        pcm_path="simple_output.pcm",
        wav_path="simple_output.wav",
        channels=1,
        sample_rate=32000,
        bits_per_sample=16,
    )
