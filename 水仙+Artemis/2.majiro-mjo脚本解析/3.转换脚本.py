import os
import re
from pathlib import Path

# 配置信息 ============================================================
CONFIG = {
    "title": "Majiro 水仙10周年脚本处理 by qianmo",
    "mjdisasm_path": r"C:\Users\Administrator\Desktop\水仙\2.majiro-mjo脚本解析\mjdisasm.exe",
    "input_dir": r"C:\Users\Administrator\Desktop\水仙\2.majiro-mjo脚本解析\mjo",
    "temp_dir": r"C:\Users\Administrator\Desktop\水仙\2.majiro-mjo脚本解析\temp",
    "work_dir": r"C:\Users\Administrator\Desktop\水仙\2.majiro-mjo脚本解析",
    "output_dir": r"C:\Users\Administrator\Desktop\水仙\2.majiro-mjo脚本解析\txt-jiaoben"
}

# 工具函数 ============================================================
def show_header():
    """显示程序标题"""
    terminal_width = 80
    title = f" {CONFIG['title']} "
    border = '=' * terminal_width
    title_line = title.center(terminal_width, '=')
    print(f"\n{border}\n{title_line}\n{border}\n")

def show_config():
    """显示配置信息"""
    print("当前配置：")
    print(f"  mjdisasm 路径：{CONFIG['mjdisasm_path']}")
    print(f"  输入目录：{CONFIG['input_dir']}")
    print(f"  临时目录：{CONFIG['temp_dir']}")
    print(f"  工作目录：{CONFIG['work_dir']}")
    print(f"  输出目录：{CONFIG['output_dir']}")
    print('\n' + '=' * 80 + '\n')

def wait_any_key(prompt="任意按键开始合并mjs和sjs文件"):
    """等待用户按键"""
    try:
        import msvcrt
        print(prompt)
        msvcrt.getch()
    except ImportError:
        input(prompt + " (按 Enter 继续)")

# 核心功能 ============================================================
def parse_sjs(sjs_path):
    """解析.sjs文件为字典（保留原始转义字符）"""
    res_dict = {}
    with open(sjs_path, 'r', encoding='utf-8') as f:
        for line in f:
            match = re.match(r'<(\d+)>\s*(.*)', line.strip())
            if match:
                num, content = match.groups()
                res_dict[num] = content
    return res_dict

def process_mjs(mjs_path, sjs_data, output_dir):
    """处理单个.mjs文件"""
    output_path = Path(output_dir) / (mjs_path.stem + ".txt")
    
    with open(mjs_path, 'r', encoding='utf-8') as infile, \
         open(output_path, 'w', encoding='utf-8') as outfile:
        
        for line in infile:
            modified_line = re.sub(
                r'#res<(\d+)>',
                lambda m: f'#res<{sjs_data.get(m.group(1), m.group(1))}>',
                line
            )
            outfile.write(modified_line)

def main():
    # 初始化目录
    input_dir = Path(CONFIG['temp_dir'])
    output_dir = Path(CONFIG['output_dir'])
    output_dir.mkdir(parents=True, exist_ok=True)

    # 处理文件
    processed = 0
    errors = 0
    
    for mjs_path in input_dir.glob("*.mjs"):
        sjs_path = mjs_path.with_suffix(".sjs")
        
        if not sjs_path.exists():
            print(f"⚠ 警告：找不到对应的.sjs文件 {sjs_path.name}")
            errors += 1
            continue

        try:
            sjs_data = parse_sjs(sjs_path)
            process_mjs(mjs_path, sjs_data, output_dir)
            print(f"✓ 已处理：{mjs_path.name}")
            processed += 1
        except Exception as e:
            print(f"✗ 处理失败：{mjs_path.name} - {str(e)}")
            errors += 1

    # 显示统计信息
    print('\n' + '=' * 80)
    print(f"处理完成：成功 {processed} 个，失败 {errors} 个")
    print('=' * 80)

if __name__ == "__main__":
    # 显示图形界面
    show_header()
    show_config()
    
    # 等待用户确认
    wait_any_key()
    
    # 执行处理流程
    main()
    
    # 退出提示
    input("\n处理完成，按 Enter 键退出...")