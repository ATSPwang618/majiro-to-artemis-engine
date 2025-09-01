import os
import re
import tkinter as tk
from tkinter import messagebox, scrolledtext, filedialog
from typing import Dict, List, Optional

# 输入和输出目录
INPUT_DIR = "mjo原生脚本提取块内容"
OUTPUT_DIR = "转录的Artemis引擎脚本"

# 用来暂存语音 ID，等待与文本合并
pending_voice: Optional[str] = None

def map_line(line: str) -> Optional[str]:
    """将一行 MJO block 内的命令映射为 AST 命令"""
    global pending_voice
    line = line.strip()

    # 处理文本命令
    if line.startswith("#res："):
        text = line.replace("#res：", "").strip(" >")
        if pending_voice:  # 如果有语音 ID，合并到文本命令中
            mapped = f'''
        --------有语音区域对话-----------
        {{"text"}},
        text = {{
            pagebreak = true,
            vo = {{{{"vo", ch="li", file="{pending_voice}"}},}},
            ja = {{{{"{text}"}},}},
        }}'''
            pending_voice = None
            return mapped
        return f'''
        --------没有语音区域对话-----------
        {{"text"}},
        text = {{
            pagebreak = true,
            ja = {{{{"{text}"}},}},
        }}'''

    # 处理背景/立绘命令
    if line.startswith("call<$a4eb1e4c"):
        m = re.search(r"\('([^']+)'", line)
        if m:
            return f'''
        {{"bg", id=1, lv=5, file="{m.group(1)}", time=1500, path=":bg/", sync=0}},
        {{"ex", time=1500, func="wait"}}'''

    # 处理背景音乐（BGM）命令
    if line.startswith("call<$d334ba75"):
        m = re.search(r"\('([^']+)'", line)
        if m:
            return f'''
        -----BGM播放区域------
        {{"SE",id=5,file="{m.group(1)}",loop=1, time=500, vol=200}}'''

    # 处理音效（SE）命令
    if line.startswith("syscall<$f62e3ca7"):
        m = re.search(r"\('([^']+)'", line)
        if m:
            return f'''
        -----SE播放区域,默认通道1播放------  
        {{"se",id=1,file="{m.group(1)}",loop=0, time=500, vol=200}}'''

    # 处理语音命令（缓存语音 ID，等待与下一条文本合并）
    if line.startswith("call<$812afdf0"):
        m = re.search(r"\('([^']+)'", line)
        if m:
            pending_voice = m.group(1)
        return None

    # 处理暂停命令
    if line.startswith("pause"):
        return '''
        {"ex", time=400, func="wait"}'''

    # 处理清屏命令
    if line.startswith("cls"):
        return '''
        --{"msgoff"}, 
        --{"cgdel",id=-1},
        --{"fg", mode=-2}'''
    # 处理退出命令
    if line.startswith("exit"):
        return ''''''
    # 未匹配的命令返回 None
    return None

def convert_blocks(lines: List[str]) -> Dict[str, List[str]]:
    """将提取的脚本行转换为 AST 块"""
    blocks: Dict[str, List[str]] = {}  # 存储所有块的字典
    current_block: Optional[str] = None  # 当前正在处理的块

    for line in lines:
        # 如果是块的起始行，创建新块
        if line.startswith("Block"):
            current_block = line.split()[1].strip(":")
            blocks[current_block] = []
            continue

        # 将块内的每一行映射为 AST 命令
        if current_block is not None:
            mapped = map_line(line)
            if mapped:
                blocks[current_block].append("    " + mapped)  # 使用4个空格缩进

    return blocks

def build_ast(blocks: Dict[str, List[str]]) -> str:
    """将所有块拼装为 AST Lua 表"""
    # 添加引擎默认头部信息
    header = '''astver = 2.0
astname = "ast"
ast = {
    block_00000 = {
        {"savetitle", text="chapter 章节"},
        {"user", mode="autosave", no=0},
        {"eval", exp="g.chap01=1"},
        {"msgoff"},
        {"cgdel", id=-1},
        {"fg", mode=-2},
        {"bg", id=1, lv=5, file="black", time=1500, path=":bg/", sync=0},
        {"ex", time=1500, func="wait"},
        -- 上面是默认区域，不要随便删除，下面开始剧情文字行的第一行消息
    },
'''
    ast_blocks: List[str] = []  # 存储所有块的字符串表示
    block_keys = sorted(blocks.keys())  # 按块的顺序排序
    for i, key in enumerate(block_keys):
        block_lines = blocks[key]  # 获取当前块的所有命令
        if key == "00000":
            # 将内容追加到 header 的默认区域
            block_str = ",\n        ".join(block_lines)
            header = header.rstrip("    },\n") + f",\n        {block_str},\n        linknext = \"block_{block_keys[i+1]}\",\n        line = 96\n    }},\n"
        elif key == block_keys[-1]:
            # 特殊处理最后一个块
            block_str = f'    block_{key} = {{\n        ' + ",\n        ".join(block_lines)
            # 删除多余的 linkback 和 line 字段
            block_str = block_str.replace(f',\n        linkback = "block_{block_keys[-2]}"', "")
            block_str = block_str.replace(f',\n        line = {96 + (len(block_keys) - 1) * 2}', "")
            # 添加结束块的特殊字段
            block_str += f''',\n        {{"msgoff"}},\n        {{"ex", time=1000, func="wait"}},\n        -----声音全部关闭\n        {{"se", stop=1, id=1, time=1000}},\n        {{"se", stop=1, id=2, time=1000}},\n        {{"se", stop=1, id=3, time=1000}},\n        {{"se", stop=1, id=4, time=1000}},\n        ------------\n        {{"bgm", stop=1, id=0, time=1000}},\n        -------------\n        {{"exreturn"}},\n        {{"text"}},\n        linkback = "block_{block_keys[-2]}",\n        line = {96 + (len(block_keys) - 1) * 2}\n    }},\n'''
            ast_blocks.append(block_str)
        else:
            # 统一缩进为4个空格
            block_str = f'    block_{key} = {{\n        ' + ",\n        ".join(block_lines)
            # 添加 linkback、linknext 和 line 信息
            if i > 0:
                block_str += f',\n        linkback = "block_{block_keys[i-1]}"'
            if i + 1 < len(block_keys):
                block_str += f',\n        linknext = "block_{block_keys[i+1]}"'
            block_str += f',\n        line = {96 + i * 2}\n    }},\n'  # 假设每个块的行号递增2
            ast_blocks.append(block_str)

    # 添加 label 块
    label_block = '''    label = {
        z00 = { block="block_00000", label=2 },
        z01 = { block="block_00000", label=46 },
        top = { block="block_00000", label=1 },
    },
'''
    return header + "".join(ast_blocks) + label_block + "}"

def remove_blank_lines(file_path: str) -> None:
    """移除文件中的所有空白行"""
    with open(file_path, "r", encoding="utf-8") as f:
        lines = f.readlines()

    # 过滤掉空白行
    non_blank_lines = [line for line in lines if line.strip()]

    with open(file_path, "w", encoding="utf-8") as f:
        f.writelines(non_blank_lines)

def process_file(input_file: str, output_file: str, log_widget):
    """处理单个文件并生成 AST"""
    with open(input_file, "r", encoding="utf-8") as f:
        lines = f.readlines()

    blocks = convert_blocks(lines)
    ast_text = build_ast(blocks)

    with open(output_file, "w", encoding="utf-8") as f:
        f.write(ast_text)

    # 移除生成文件中的空白行
    remove_blank_lines(output_file)

    log_widget.insert(tk.END, f"转换完成: {input_file} -> {output_file}\n")
    log_widget.see(tk.END)

# 修改为单文件处理模式
def start_processing():
    input_file = filedialog.askopenfilename(title="选择输入文件", filetypes=[("Text Files", "*.txt")])
    if not input_file:
        messagebox.showerror("错误", "未选择输入文件！")
        return

    # 修改输出文件名逻辑
    output_file_name = os.path.basename(input_file).replace("decrypted_", "").replace("-parsed_blocks", "")
    output_file_name = os.path.splitext(output_file_name)[0] + ".ast"
    output_file = os.path.join(OUTPUT_DIR, output_file_name)
    os.makedirs(OUTPUT_DIR, exist_ok=True)

    log_widget.delete(1.0, tk.END)
    process_file(input_file, output_file, log_widget)

    messagebox.showinfo("完成", f"文件转换完成！\n输入: {input_file}\n输出: {output_file}")

# 创建 GUI 界面
root = tk.Tk()
root.title("MJO 转换工具")

frame = tk.Frame(root)
frame.pack(padx=10, pady=10)

label = tk.Label(frame, text="点击下方按钮选择文件并开始转换:")
label.pack()

start_button = tk.Button(frame, text="选择文件并开始转换", command=start_processing)
start_button.pack(pady=5)

log_widget = scrolledtext.ScrolledText(frame, width=80, height=20, state='normal')
log_widget.pack(pady=5)

root.mainloop()
