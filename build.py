import PyInstaller.__main__
import os

# 获取当前目录
current_dir = os.path.dirname(os.path.abspath(__file__))

PyInstaller.__main__.run([
    'main.py',  # 主程序
    '--name=VideoProcessor',  # 生成的exe名称
    '--windowed',  # 使用GUI模式
    '--onedir',  # 生成单文件夹
    '--add-data=scripts;scripts',  # 添加scripts文件夹
    '--icon=assets/icon.ico',  # 如果你有图标的话
    '--clean',  # 清理临时文件
    '--noconfirm',  # 不确认覆盖
    f'--workpath={os.path.join(current_dir, "build")}',  # 设置构建目录
    f'--distpath={os.path.join(current_dir, "dist")}',  # 设置输出目录
]) 