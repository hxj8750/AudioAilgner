import re
import textgrid
import os

current_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

input_subtitle_path = os.path.join(current_dir,"./training/output.txt")
input_textgrid_path = os.path.join(current_dir,"./temp/output.TextGrid")
output_subtitle_path = os.path.join(current_dir,"./temp/temp_subtitle.srt")

# 读取文本文件
with open(input_subtitle_path, "r", encoding="utf-8") as file:
    lines = file.readlines()

# 创建一个二维列表来存储结果
result = []

for line in lines:
    # 去除行首尾的空白字符
    line = line.strip()
    if not line:  # 跳过空行
        continue

    # 使用正则表达式分割单词和连词，同时忽略末尾的标点符号
    words = re.findall(r"[a-zA-Z]+(?:'[a-zA-Z]+)?\d*|\d+(?:/\d+)?", line)
    result.append(words)

# 读取原始 TextGrid 文件
tg = textgrid.TextGrid.fromFile(input_textgrid_path)
# 获取需要处理的 tier（假设是第一个 tier，名为 "words"）
tier = tg.getFirst("words")

def parse_time(srt_time):
   """解析 SRT 时间字符串为秒数"""
   hours, minutes, seconds, millis = map(int, re.split(r'[:,]', srt_time))
   return hours * 3600 + minutes * 60 + seconds + millis / 1000

# 定义一个函数，将时间（秒）转换为 SRT 格式的时间字符串
def format_time(seconds):
    millis = int((seconds % 1) * 1000)
    seconds = int(seconds)
    mins, secs = divmod(seconds, 60)
    hours, mins = divmod(mins, 60)
    return f"{hours:02}:{mins:02}:{secs:02},{millis:03}"

# print(result[147])

# 生成 SRT 文件内容
srt_content = []
wrong_content = []
srt_index = 1
interval_index = 0  # 当前 TextGrid 间隔索引
tier_intervals = tier.intervals  # 获取 tier 中的所有间隔

for words in result:
    subtitle_start = None
    subtitle_end = None
    interval_index_backup = interval_index  # 备份当前 index
    temp_list = []

    # 遍历字幕行中的每个单词
    for word in words:
        found = False
        temp_start = None
        temp_end = None
        temp_word = ""  # 临时拼接单词

        # 只要interval_index小于tier_intervals的长度，就继续拼接
        while interval_index < len(tier_intervals):
            interval = tier_intervals[interval_index]
            # 获取当前text
            mark = interval.mark.strip()

            # 跳过空标记
            if not mark:
                interval_index += 1
                continue

            # 拼接当前标记
            temp_word += mark

            # 更新当前字幕块的起始时间和结束时间
            if temp_start is None:
                temp_start = interval.minTime
            temp_end = interval.maxTime

            # 如果拼接结果与目标单词匹配
            if temp_word.lower() == word.lower():
                found = True
                # print(f"匹配成功：{temp_word}")
                # 如果当前字幕块还没有起始时间，则更新起始时间
                if subtitle_start is None:
                    subtitle_start = temp_start
                # 更新字幕块的结束时间
                subtitle_end = temp_end
                # 移动到下一个间隔
                interval_index += 1
                interval_index_backup += 1
                temp_list.append(temp_word)
                break
            elif temp_word.lower() not in word.lower():  # 如果拼接结果不在匹配目标单词,比如"I'm"和"I"属于在的情况
                #print(f"将重置：{temp_word}")
                temp_word = ""  # 重置拼接状态
                temp_start = None
                temp_end = None
                interval_index += 1
            else:
                # print(f"继续拼接：{temp_word}")
                interval_index += 1  # 继续拼接下一个标记

        # 如果没有找到匹配项，回退到备份点
        if not found:
            interval_index = interval_index_backup
            break
    
    if [word.lower() for word in temp_list] == [word.lower() for word in words]:
        pass
    else:
        print(f"未匹配的字幕行: {' '.join(words)}")
        print(f"匹配结果: {' '.join(temp_list)}")
        wrong_content.append(f"{srt_index}")

    # 如果找到时间区间，将其写入 SRT 内容
    if subtitle_start is not None and subtitle_end is not None:
        # print(f"起始时间：{format_time(subtitle_start)}")
        # print(f"结束时间：{format_time(subtitle_end)}")
        srt_content.append(f"{srt_index}")
        srt_content.append(
            f"{format_time(subtitle_start)} --> {format_time(subtitle_end)}"
        )
        srt_content.append(" ".join(words))  # 将单词列表拼接成字幕行
        srt_content.append("")  # 添加空行分隔
        srt_index += 1
    # else:
    #     print(f"subtitle_start: {subtitle_start}")
    #     print(f"subtitle_end: {subtitle_end}")
    #     print(f"未匹配的字幕行: {' '.join(words)}")

if wrong_content:
    print(f"有问题的字幕行: {wrong_content}")

    for index in wrong_content:
        index = int(index) - 1
        # 解析前一个 content 的 subtitle_end
        prev_time_str = srt_content[int(index) * 4 - 3]
        prev_end_time = parse_time(prev_time_str.split(" --> ")[1])
            # 解析后一个 content 的 subtitle_start
        next_time_str = srt_content[int(index) * 4 + 5]
        next_start_time = parse_time(next_time_str.split(" --> ")[0])
            # 更新当前 content 的时间
        srt_content[int(index) * 4 + 1] = f"{format_time(prev_end_time)} --> {format_time(next_start_time)}"

    print("已对错误字幕行进行修正")

# 将 SRT 内容写入文件
with open(output_subtitle_path, "w", encoding="utf-8") as srt_file:
    srt_file.write("\n".join(srt_content))

print(f"SRT 文件已生成：{output_subtitle_path}")    

