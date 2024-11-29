import os
import itertools
from pydub import AudioSegment
from pydub.silence import detect_nonsilent
from decimal import Decimal, getcontext

# 设置 Decimal 的全局精度
getcontext().prec = 20

def split_on_silence_hxj(audio_segment, min_silence_len=1000, silence_thresh=-16, keep_silence=100,
                     seek_step=1):
    """
    根据检测到的静音段，将输入的音频切割为多个非静音音频段。

    参数:
    - audio_segment: pydub.AudioSegment
        需要切割的原始音频段。

    - min_silence_len: int (默认值: 1000)
        将音频段视为静音的最短时长（单位: 毫秒）。

    - silence_thresh: int (默认值: -16)
        判定为静音的音量阈值（单位: dBFS）。低于该值的音频被视为静音。

    - keep_silence: int, bool (默认值: 100)
        - 如果为 int：指定在每个非静音段的开头和结尾保留的静音时长（单位: 毫秒）。
        - 如果为 True：保留所有静音段。
        - 如果为 False：完全不保留静音段。

    - seek_step: int (默认值: 1)
        检测静音时的步进大小（单位: 毫秒）。

    返回:
    - (List of pydub.AudioSegment, List of tuple)
        返回两部分内容：
        1. 包含所有非静音段的列表，每段可能包含两侧保留的静音。
        2. 静音段的时间点列表，格式为 [(start1, end1), (start2, end2), ...]。
    """

    # 内部辅助函数，用于将一个可迭代对象转为相邻元素的配对
    def pairwise(iterable):
        """
        将输入可迭代对象的元素两两配对。
        示例: s -> (s0, s1), (s1, s2), (s2, s3), ...
        """
        a, b = itertools.tee(iterable)  # 创建两个迭代器
        next(b, None)  # 将第二个迭代器前移一位
        return zip(a, b)  # 返回两个迭代器的配对

    # 如果 keep_silence 是布尔值，转换为相应的静音时长
    if isinstance(keep_silence, bool):
        keep_silence = len(audio_segment) if keep_silence else 0

    # 检测非静音段，生成初步切割范围，并在两侧添加静音缓冲
    output_ranges = [
        [start - keep_silence, end + keep_silence]  # 扩展非静音段的起点和终点
        for (start, end)
        in detect_nonsilent(audio_segment, min_silence_len, silence_thresh, seek_step)  # 调用检测非静音段的函数
    ]

    # 处理相邻的切割范围，如果因保留静音导致范围重叠，调整范围边界
    for range_i, range_ii in pairwise(output_ranges):
        last_end = range_i[1]  # 当前段的终点
        next_start = range_ii[0]  # 下一段的起点
        if next_start < last_end:  # 如果下一段的起点在当前段的终点之前，说明范围重叠
            # 将重叠部分平分给两个段落
            range_i[1] = (last_end + next_start) // 2
            range_ii[0] = range_i[1]

    # 静音段时间点列表
    silence_ranges = []
    last_end = 0  # 记录上一个非静音段的结束时间
    for start, end in output_ranges:
        if start > last_end:  # 如果当前非静音段的起点晚于上一个段的终点，则存在静音段
            silence_ranges.append((last_end, start))  # 记录静音段时间
        last_end = end  # 更新上一个非静音段的结束时间

    # 如果最后一个非静音段的结束时间小于音频总长度，记录尾部静音
    if last_end < len(audio_segment):
        silence_ranges.append((last_end, len(audio_segment)))

    # 根据调整后的切割范围，从原始音频中提取对应的非静音段
    non_silent_segments = [
        audio_segment[max(start, 0):min(end, len(audio_segment))]  # 确保范围在音频长度范围内
        for start, end in output_ranges
    ]

    return non_silent_segments, silence_ranges

current_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
# 输入和输出文件
input_audio = os.path.join(current_dir,"./temp/temp_output.wav")
output_audio_path = os.path.join(current_dir,"./training/output.wav")
time_log = os.path.join(current_dir,"./temp/silence_timestamps.txt")

# 加载音频
audio = AudioSegment.from_file(input_audio, format="wav")

# 静音检测参数
silence_thresh = -40  # 静音阈值（单位：dBFS）
min_silence_len = 25  # 最短静音持续时间（单位：ms）
buffer_ms = 100  # 每个片段开头和结尾保留 100 毫秒的静音
silence_list = []

# 使用 split_on_silence 进行音频剪辑
chunks, silence_list = split_on_silence_hxj(
    audio,
    min_silence_len=min_silence_len,  # 与 detect_silence 参数一致
    silence_thresh=silence_thresh,  # 与 detect_silence 参数一致
    keep_silence=buffer_ms
)

# 合并切割后的音频片段
if chunks:  # 确保有片段返回
    processed_audio = chunks[0]
    for chunk in chunks[1:]:
        processed_audio += chunk
else:
    processed_audio = audio  # 如果没有检测到静音，保留原始音频

# 导出剪辑后的音频
processed_audio.export(output_audio_path, format="wav")
print(f"剪辑后的音频已保存到：{output_audio_path}")


# 转换为 Decimal 并保存高精度时间
silences = [(Decimal(start) / 1000, Decimal(end) / 1000) for start, end in silence_list]

# 保存静音时间点日志
with open(time_log, "w", encoding="utf-8") as f:
    for start, end in silences:
        f.write(f"Start: {start:.6f}, End: {end:.6f}\n")

print(f"静音时间点已保存到：{time_log}")
