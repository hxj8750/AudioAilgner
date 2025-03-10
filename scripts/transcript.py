import os
import sys
import yt_dlp
from youtube_transcript_api import YouTubeTranscriptApi

def download_source(video_id):
    ret = []

    video_id = video_id
    video_url = f"https://www.youtube.com/watch?v={video_id}"

    current_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

    # 指定视频和字幕的存储位置
    subtitle_path = os.path.join(current_dir,"./res/subtitles_en.txt")
    video_path = os.path.join(current_dir,"./res/")

    # yt-dlp 下载设置
    ydl_opts = {
        'format': 'best',  # 下载最佳视频质量
        'outtmpl': f"{video_path}raw_video.mp4",  # 输出文件名为raw_video.mp4
        'retries': 100,  # 设置重试次数
    }

    try:
    # 下载英文字幕
        transcript_en = YouTubeTranscriptApi.get_transcript(video_id, languages=['en'])
    except Exception as e:
        ret.append(f"字幕下载失败:{e}")
    else:
        # 将字幕提取为纯文本
        with open(subtitle_path, "w", encoding="utf-8") as file:
            for line in transcript_en:
                file.write(f"{line['text']}\n")
        ret.append("英文字幕下载完成")

    try:
    # 下载视频
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            ydl.download([video_url])
    except Exception as e:
                ret.append(f"视频下载失败:{e}")
    else:
        ret.append("视频下载完成")

    return ret

