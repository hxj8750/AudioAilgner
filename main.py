from PySide6.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, 
                             QPushButton, QLabel, QTextEdit, QFrame, QHBoxLayout, 
                             QInputDialog, QLineEdit, QMessageBox)
from PySide6.QtCore import Qt
from PySide6.QtGui import QFont, QColor, QIcon
import sys
from datetime import datetime

from scripts.transcript import download_source
from scripts.init import clear_folder

import subprocess
import re

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.download_video_script_path = "./scripts/transcript.py"
        self.extract_audio_script_path = "./scripts/video_audio_cutter.py"
        self.remove_silence_script_path = "./scripts/remove_silence.py"
        self.generate_subtitle_script_path = "./scripts/generate_srt.py"
        self.adjust_timeline_script_path = "./scripts/adjust.py"

        self.setWindowTitle("SubSyncer")
        
        # 设置窗口大小和位置
        self.resize(800, 600)
        screen = QApplication.primaryScreen().geometry()
        self.move((screen.width() - self.width()) // 2,
                 (screen.height() - self.height()) // 2)
        
        # 创建主布局
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QHBoxLayout(central_widget)
        main_layout.setSpacing(0)
        main_layout.setContentsMargins(0, 0, 0, 0)
        
        # 创建左侧面板
        left_panel = QWidget()
        left_panel.setFixedWidth(250)
        left_panel.setStyleSheet("""
            QWidget {
                background-color: #2c3e50;
                color: white;
            }
        """)
        left_layout = QVBoxLayout(left_panel)
        left_layout.setSpacing(5)
        left_layout.setContentsMargins(20, 30, 20, 30)
        
        # 添加标题
        title = QLabel("SubSyncer")
        title.setFont(QFont("Microsoft YaHei UI", 16))
        title.setAlignment(Qt.AlignLeft)
        title.setStyleSheet("color: white; margin-bottom: 20px;")
        left_layout.addWidget(title)
        
        # 创建功能按钮
        buttons_info = [
            ("下载视频", "从网站下载视频和原始字幕", self.download_video),
            ("提取音频", "从视频中提取音频", self.extract_audio),
            ("自动换行", "自动分行后的字幕文件导入到文件夹", self.import_subtitle),
            ("生成时间轴", "生成包含逐字时间轴的textgrid文件", self.generate_timeline),
            ("生成字幕", "生成srt字幕文件", self.generate_subtitle),
            ("初始化","删除所有临时文件", self.init)
        ]
        
        for text, tooltip, slot in buttons_info:
            btn = QPushButton(text)
            btn.setToolTip(tooltip)
            btn.setFont(QFont("Microsoft YaHei UI", 10))
            btn.setCursor(Qt.PointingHandCursor)
            btn.clicked.connect(slot)
            btn.setStyleSheet("""
                QPushButton {
                    background-color: transparent;
                    color: #ecf0f1;
                    border: none;
                    text-align: left;
                    padding: 12px 15px;
                    border-radius: 5px;
                }
                QPushButton:hover {
                    background-color: #34495e;
                }
                QPushButton:pressed {
                    background-color: #2980b9;
                }
            """)
            left_layout.addWidget(btn)
        
        left_layout.addStretch()
        main_layout.addWidget(left_panel)
        
        # 创建右侧内容区
        right_panel = QWidget()
        right_panel.setStyleSheet("""
            QWidget {
                background-color: #f5f6fa;
            }
        """)
        right_layout = QVBoxLayout(right_panel)
        right_layout.setSpacing(20)
        right_layout.setContentsMargins(30, 30, 30, 30)
        
        # 添加状态标签
        status_label = QLabel("处理状态")
        status_label.setFont(QFont("Microsoft YaHei UI", 12))
        status_label.setStyleSheet("color: #2c3e50;")
        right_layout.addWidget(status_label)
        
        # 创建状态文本框
        self.status_text = QTextEdit()
        self.status_text.setReadOnly(True)
        self.status_text.setFont(QFont("Consolas", 10))
        self.status_text.setStyleSheet("""
            QTextEdit {
                background-color: white;
                border: none;
                border-radius: 5px;
                padding: 15px;
            }
        """)
        right_layout.addWidget(self.status_text)
        
        main_layout.addWidget(right_panel)
        
        # 设置窗口样式
        self.setStyleSheet("""
            QMainWindow {
                background-color: #f5f6fa;
            }
            QToolTip {
                background-color: #2c3e50;
                color: white;
                border: none;
                padding: 5px;
            }
        """)
        
        # 初始化状态信息
        self.log_message("欢迎使用视频处理工具")
    
    def log_message(self, message):
        """添加状态信息"""
        timestamp = datetime.now().strftime("%H:%M:%S")
        self.status_text.append(f"<span style='color:#95a5a6'>[{timestamp}]</span> {message}")

    def show_confirm_dialog(self, title, ask):
        msg_box = QMessageBox(self)
        msg_box.setWindowTitle(title)
        msg_box.setText(ask)
        msg_box.setStandardButtons(QMessageBox.Yes | QMessageBox.No)
        msg_box.setIcon(QMessageBox.Question)

        return msg_box.exec()
    
    def download_video(self):
        rets = []
        # 要求用户输入视频id，如果用户关闭输入框，则什么都不做
        video_id, ok = QInputDialog.getText(self, "输入视频ID", "请输入视频ID:")
        if ok and video_id:
            rets = download_source(video_id)
            for ret in rets:
                self.log_message(ret)

    
    def extract_audio(self):
        self.log_message("开始提取音频...")
        try:
            subprocess.run(["python", self.extract_audio_script_path])
        except Exception as e:
            self.log_message(f"提取音频失败: {e}")
        else:
            self.log_message("提取音频完成")

        try:
            subprocess.run(["python", self.remove_silence_script_path])
        except Exception as e:
            self.log_message(f"移除静音失败: {e}")
        else:
            self.log_message("移除静音完成")
    
    # 该函数有问题，len(text)是字符的长度，而不是单词的个数，有空再处理

    def split_text(self,text):
        # 将长文本分割为若干个单词的片段，平均每个单词有四个字符
        length = len(text)
        number = 1000
        segs = []
        seg_num = length // number
        start = 0

        # 如果文本长度低于1000，直接返回原始文本
        if length <= number:
            segs.append(text)
            return segs

        for i in range(1,seg_num+1):
            end = start + number
            # 如果到最后一段，end直接等于全文最后一个字符
            if i == seg_num:
                end = length
            
            #  如果text[end]位于一个单词的中间，就继续往后扫描
            while text[end-1] != " " and text[end-1] != "\n":
                end += 1
            # 将该片段写入列表
            segs.append([end,text[start:end]])
            start = end # 如果end已经是全文最后的字符，则下一次循环不可能执行

        return segs
    
    def replace_newlines_with_spaces(self,str):
        # 将所有换行替换为空格
        input_str = str
        output_str = re.sub(r'\n',' ',input_str)

        return output_str
    
    def clean_text(self,text):
        # 将 '-' 替换为空格
        text = text.replace('-', ' ')
        # 将双空格替换为单空格（可以用 replace 或正则表达式）
        while '  ' in text:
            text = text.replace('  ', ' ')
        # 将中文单引号替换为英文单引号
        text = text.replace('‘', "'")
        text = text.replace('’', "'")
        return text

    def import_subtitle(self):
        # 读取subtitles_en.txt
        with open("./res/subtitles_en.txt",'r') as file:
            content = file.read()
        # 分段
        segment = self.split_text(content)
        print(segment)
        # 去除换行
        for i in range(0,len(segment)):
            segment[i][1] = self.replace_newlines_with_spaces(segment[i][1])

        # 多进程
        processes = []
        only_segment = []
        # 将纯文本片段写入only_segment
        for i in range(0,len(segment)):
            only_segment.append(segment[i][1])
        # 分配进程
        for i, seg in enumerate(only_segment):
            p = subprocess.Popen(["python","./scripts/punctuation_predict.py"],
                                 stdin=subprocess.PIPE,
                                 stdout=subprocess.PIPE,
                                 stderr=subprocess.PIPE,
                                 text=True
                                 )
            p.stdin.write(seg)
            p.stdin.close()
            processes.append((i,p))
        
        # 等待进程完成
        results = []
        for i,p in processes:
            out,err = p.communicate()
            results.append((i,out,err,p.returncode))
        
        text = ""
        # 合并
        for item in results:
            text += item[1]

        # 为text添加换行符
        i = 0
        num = 0
        new_text = ""
        while i < len(text):
            if text[i] in ['.','?','!']:
                new_text += '\n'
                i += 2
                num = 0
            # 如果一行过长，则在逗号处分行
            elif text[i] == ',':
                if num < 25:
                    new_text += text[i]
                    i += 1
                    num += 1      
                else:
                    new_text += '\n'
                    i += 2
                    num = 0           
            else:
                new_text += text[i]
                i += 1
                num += 1
        
        new_text = self.clean_text(new_text)

        # 写入
        with open("./training/output.txt",'w') as file:
            file.write(new_text)
        
        self.log_message("done")


    def generate_timeline(self):
        self.log_message("开始生成时间轴...")
        command = [
            "mfa",  # MFA 命令
            "align",  # 子命令
            "./training",  # 输入文件夹路径
            "english_mfa",  # 使用的字典
            "english_mfa",  # 声学模型
            "./temp",  # 输出路径
            "--beam", "50",  # 设置 beam 参数
            "--retry_beam", "400"  # 设置 retry_beam 参数
            ]
        try:
            subprocess.run(command)
        except Exception as e:
            self.log_message(f"生成时间轴失败: {e}")
        else:
            self.log_message("生成时间轴完成")
    
    def generate_subtitle(self):
        self.log_message("开始生成字幕...")
        try:
            subprocess.run(["python", self.generate_subtitle_script_path])
        except Exception as e:
            self.log_message(f"生成字幕失败: {e}")
        else:
            self.log_message("生成字幕完成")
        
        try:
            subprocess.run(["python", self.adjust_timeline_script_path])
        except Exception as e:
            self.log_message(f"调整时间轴失败: {e}")
        else:
            self.log_message("调整时间轴完成,srt字幕文件生成完成")

    def init(self):
        result = self.show_confirm_dialog("确定要初始化吗","该操作将删除所有资源和临时文件")
        if result == QMessageBox.Yes:
            paths = [
                "./res",
                "./temp",
                "./training",
                "D:/MFA/training"
            ]
            for path in paths:
                ret = clear_folder(path)
                self.log_message(ret)
            
            # 删除__pycache__文件
            ret = clear_folder('./scripts',True)
            self.log_message(ret)


def main():
    app = QApplication(sys.argv)
    
    # 设置应用程序样式
    app.setStyle("Fusion")
    
    window = MainWindow()
    window.show()
    sys.exit(app.exec())

if __name__ == "__main__":
    main()

