import os

current_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

def remove_colon_content(input_file, output_file):
    with open(input_file, 'r', encoding='utf-8') as infile, open(output_file, 'w', encoding='utf-8') as outfile:
        for line in infile:
            # 检查是否包含冒号
            if ':' in line:
                # 分割每行，保留冒号右侧的内容
                cleaned_line = line.split(':', 1)[1].strip() + '\n'
            else:
                # 如果没有冒号，保留整行
                cleaned_line = line
            outfile.write(cleaned_line)

input_file = os.path.join(current_dir,"./temp/temp_output_txt.txt")
output_file = os.path.join(current_dir,"./training/output.txt")

remove_colon_content(input_file, output_file)

print(f"处理完成，结果已保存到 {output_file}")
