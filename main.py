from PySide6.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, 
                             QPushButton, QLabel, QTextEdit, QFrame, QHBoxLayout, QInputDialog, QLineEdit)
from PySide6.QtCore import Qt
from PySide6.QtGui import QFont, QColor, QIcon
import sys
from datetime import datetime

from scripts.transcript import download_source

import subprocess

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.download_video_script_path = "./scripts/transcript.py"
        self.extract_audio_script_path = "./scripts/video_audio_cutter.py"
        self.remove_silence_script_path = "./scripts/remove_silence.py"
        self.generate_subtitle_script_path = "./scripts/generate_srt.py"
        self.adjust_timeline_script_path = "./scripts/adjust.py"

        self.setWindowTitle("视频处理工具")
        
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
        title = QLabel("视频处理工具")
        title.setFont(QFont("Microsoft YaHei UI", 16))
        title.setAlignment(Qt.AlignLeft)
        title.setStyleSheet("color: white; margin-bottom: 20px;")
        left_layout.addWidget(title)
        
        # 创建功能按钮
        buttons_info = [
            ("下载视频", "从网站下载视频和原始字幕", self.download_video),
            ("提取音频", "从视频中提取音频", self.extract_audio),
            ("导入字幕", "将分行后的字幕文件导入到文件夹", self.import_subtitle),
            ("生成时间轴", "生成包含逐字时间轴的textgrid文件", self.generate_timeline),
            ("生成字幕", "生成srt字幕文件", self.generate_subtitle)
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
    
    def download_video(self):
        rets = []
        # 要求用户输入视频id，如果用户关闭输入框，则什么都不做
        video_id, ok = QInputDialog.getText(self, "输入视频ID", "请输入视频ID:")
        if ok and video_id:
            self.log_message(f"开始下载视频和字幕...{video_id}")
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

    def import_subtitle(self):
        # 要求用户输入发行后的字幕文件
        dialog = QInputDialog(self)
        dialog.setWindowTitle("输入分行完成的字幕文本")
        dialog.setLabelText("请直接粘贴分行后的字幕文本(推荐使用chatgpt分行):")
        dialog.setOption(QInputDialog.UsePlainTextEditForTextInput)  # 使用多行文本输入框
        dialog.resize(800, 600)  # 调整输入框大小
        ok = dialog.exec()
        subtitle_text = dialog.textValue()
        if ok and subtitle_text:
            self.log_message("开始导入字幕...")
            # 将文本保存到./training/output.txt
            with open("./training/output.txt", "w") as f:
                f.write(subtitle_text)
            self.log_message("导入字幕完成")

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

def main():
    app = QApplication(sys.argv)
    
    # 设置应用程序样式
    app.setStyle("Fusion")
    
    window = MainWindow()
    window.show()
    sys.exit(app.exec())

if __name__ == "__main__":
    main()

