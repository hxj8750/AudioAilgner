import os
from decimal import Decimal, getcontext

current_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# 设置全局精度
getcontext().prec = 20

time_file_path = os.path.join(current_dir,"./temp/temp_subtitle.srt")
silence_file_path = os.path.join(current_dir,"./temp/silence_timestamps.txt")
output_file_path = os.path.join(current_dir,"./res/output.srt")

# 将 SRT 时间格式转换为 Decimal 秒
def srt_time_to_seconds(time_str):
    hours, minutes, seconds = time_str.split(":")
    seconds, milliseconds = seconds.split(",")
    return (
        Decimal(hours) * 3600
        + Decimal(minutes) * 60
        + Decimal(seconds)
        + Decimal(milliseconds) / 1000
    )

# 从静音文件中提取开始时间和持续时间
def extract_time_and_duration(file_path):
    time_list = []
    with open(file_path, 'r') as file:
        for line in file:
            if line.startswith("Start:"):
                parts = line.strip().split(", ")
                start = Decimal(parts[0].split(": ")[1])
                end = Decimal(parts[1].split(": ")[1])
                duration = round(end - start, 3)  # 计算持续时间，保留3位小数
                time_list.append((start, duration))
    return time_list

# 从 SRT 文件中提取时间戳
time_list = []
with open(time_file_path, 'r') as file:
    for line in file:
        if '-->' in line:
            start, end = line.strip().split(' --> ')
            time_list.append(srt_time_to_seconds(start))
            time_list.append(srt_time_to_seconds(end))
# print("time_list:", time_list)

silence_durations = extract_time_and_duration(silence_file_path)
# print("silence_durations:", silence_durations)
# print("len:", len(silence_durations))
# print("sum:", sum(duration for _, duration in silence_durations))

# 根据静音持续时间调整 time_list
for start, duration in silence_durations:
    for i in range(len(time_list)):
        if start <= time_list[i]:
            # 将持续时间添加到所有后续时间戳上，精度高
            time_list[i:] = [time + duration for time in time_list[i:]]
            break

# 将调整后的 Decimal 时间戳转换回 SRT 格式
def seconds_to_srt_time(seconds):
    hours = int(seconds // Decimal(3600))
    minutes = int((seconds % Decimal(3600)) // Decimal(60))
    seconds = seconds % Decimal(60)
    milliseconds = int((seconds - int(seconds)) * 1000)
    return f"{hours:02}:{minutes:02}:{int(seconds):02},{milliseconds:03}"

# 将调整后的 Decimal 时间戳转换回 SRT 格式
srt_time_list = []
for i in range(0, len(time_list), 2):
    if i + 1 < len(time_list):  # Ensure there's a valid end time
        start_srt = seconds_to_srt_time(time_list[i])
        end_srt = seconds_to_srt_time(time_list[i + 1])
        srt_time_list.append(f"{start_srt} --> {end_srt}")

# 将调整后的 Decimal 时间戳转换回 SRT 格式
srt_time_list = []
for i in range(0, len(time_list), 2):
    if i + 1 < len(time_list):  # 确保有有效的结束时间
        start_srt = seconds_to_srt_time(time_list[i])
        end_srt = seconds_to_srt_time(time_list[i + 1])
        srt_time_list.append(f"{start_srt} --> {end_srt}")

# 将调整后的 SRT 数据写回输出文件
with open(time_file_path, 'r') as infile, open(output_file_path, 'w') as outfile:
    line_index = 0  # 跟踪要使用的 SRT 时间戳
    for line in infile:
        if '-->' in line:
            # 用调整后的值替换时间戳行
            if line_index < len(srt_time_list):
                outfile.write(srt_time_list[line_index] + '\n')
                line_index += 1
        else:
            # 写入非时间戳行
            outfile.write(line)

print(f"调整后的 SRT 文件已保存到: {output_file_path}")
