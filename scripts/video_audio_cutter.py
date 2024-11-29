import ffmpeg
import os

current_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

video_file = os.path.join(current_dir, "./res/raw_video.mp4")
audio_file = os.path.join(current_dir, "./temp/temp_output.wav")

video_file = os.path.abspath(video_file)
audio_file = os.path.abspath(audio_file)
# 提取音频
try:
    print("正在提取音频...")
    ffmpeg.input(video_file).output(audio_file, acodec="pcm_s16le", ar=16000).run(overwrite_output=True)
    print(f"音频提取完成，保存为：{audio_file}")
except ffmpeg.Error as e:
    print("提取音频失败：", e.stderr.decode())
    exit()

