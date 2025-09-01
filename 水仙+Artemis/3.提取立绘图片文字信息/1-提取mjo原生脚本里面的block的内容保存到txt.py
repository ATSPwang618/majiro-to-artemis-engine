import os
import tkinter as tk
from tkinter import messagebox, scrolledtext
from typing import Dict

def parse_blocks(file_path: str) -> Dict[str, str]:
    """
    解析文件内容并根据 #res： 标记划分块。

    Args:
        file_path (str): 输入文件路径。

    Returns:
        dict: 包含块编号和对应内容的字典。
    """
    blocks: Dict[str, str] = {}  # 存储块编号和内容
    current_block: list[str] = []  # 当前块内容
    block_number: int = 0  # 块编号

    with open(file_path, 'r', encoding='utf-8') as file:
        lines = file.readlines()

    for line in lines:
        line = line.strip()

        if line.startswith('#res：'):
            current_block.append(line)  # 先将 #res： 行加入当前块
            # 保存当前块内容
            if current_block:
                block_id = f"{block_number:05d}"
                blocks[block_id] = '\n'.join(current_block)
                current_block = []  # 清空当前块
                block_number += 1  # 块编号递增
        else:
            current_block.append(line)  # 添加行到当前块

    # 保存最后一个块
    if current_block:
        block_id = f"{block_number:05d}"
        blocks[block_id] = '\n'.join(current_block)

    return blocks

def process_directory(input_dir: str, output_dir: str, log_widget):
    """
    批量处理指定目录及其子目录中的所有 .txt 文件。

    Args:
        input_dir (str): 输入目录路径。
        output_dir (str): 输出目录路径。
        log_widget: 用于显示日志的文本框。
    """
    for root, _, files in os.walk(input_dir):
        for file in files:
            if file.endswith('.txt'):
                input_file = os.path.join(root, file)
                relative_path = os.path.relpath(root, input_dir)
                output_subdir = os.path.join(output_dir, relative_path)
                os.makedirs(output_subdir, exist_ok=True)
                output_file = os.path.join(output_subdir, f"{os.path.splitext(file)[0]}-parsed_blocks.txt")

                # 解析块
                parsed_blocks: Dict[str, str] = parse_blocks(input_file)

                # 写入到输出文件
                with open(output_file, 'w', encoding='utf-8') as out_file:
                    for block_id, content in parsed_blocks.items():
                        out_file.write(f"Block {block_id}:\n")
                        out_file.write(content + "\n\n")

                log_widget.insert(tk.END, f"解析完成: {input_file} -> {output_file}\n")
                log_widget.see(tk.END)

    messagebox.showinfo("完成", "所有文件解析完成！")

def start_processing():
    input_directory = "mjo原生脚本"
    output_directory = "mjo原生脚本提取块内容"

    if not os.path.exists(input_directory):
        messagebox.showerror("错误", f"输入目录不存在: {input_directory}")
        return

    os.makedirs(output_directory, exist_ok=True)
    log_widget.delete(1.0, tk.END)
    process_directory(input_directory, output_directory, log_widget)

# 创建 GUI 界面
root = tk.Tk()
root.title("MJO 脚本解析工具")

frame = tk.Frame(root)
frame.pack(padx=10, pady=10)

label = tk.Label(frame, text="点击下方按钮开始解析:")
label.pack()

start_button = tk.Button(frame, text="开始解析", command=start_processing)
start_button.pack(pady=5)

log_widget = scrolledtext.ScrolledText(frame, width=80, height=20, state='normal')
log_widget.pack(pady=5)

root.mainloop()
