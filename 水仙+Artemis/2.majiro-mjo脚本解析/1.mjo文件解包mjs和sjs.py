import os
import shutil
import subprocess
import msvcrt
from collections import defaultdict

# ==== 配置部分 ====
mjdisasm_path = r"C:\Users\Administrator\Desktop\水仙\2.majiro-mjo脚本解析\mjdisasm.exe"
input_dir = r"C:\Users\Administrator\Desktop\水仙\2.majiro-mjo脚本解析\mjo"
temp_file_dir = r"C:\Users\Administrator\Desktop\水仙\2.majiro-mjo脚本解析\temp"
mjdisasm_work_dir = os.path.dirname(mjdisasm_path)

# ==== 辅助函数 ====
def press_any_key(prompt="按任意键继续..."):
    print(f"\n{prompt}", end='', flush=True)
    msvcrt.getch()
    print()

def print_header(title):
    border = "=" * 60
    print(f"\n{border}\n{title.center(60)}\n{border}")

def print_debug(info, indent=1, bullet=""):
    prefix = "  " * indent
    if bullet:
        prefix += f"{bullet} "
    print(f"{prefix}{info}")

    # ==== 主函数 ====
def disasm_mjo_files():
    print_header("Majiro 水仙10周年脚本处理 by qianmo")
    print_debug("当前配置：", 0)
    print_debug(f"mjdisasm 路径：{mjdisasm_path}")
    print_debug(f"输入目录：{input_dir}")
    print_debug(f"临时目录：{temp_file_dir}")
    print_debug(f"工作目录：{mjdisasm_work_dir}")
    
    # 初始化记录器
    result_log = {
        'success': [],
        'failed': defaultdict(list)
    }

    press_any_key("任意按键开始处理 .mjo 文件")

    # 创建目录结构
    os.makedirs(temp_file_dir, exist_ok=True)
    print_debug(f"创建临时目录：{temp_file_dir}")

    try:
        mjo_files = [f for f in os.listdir(input_dir) if f.lower().endswith(".mjo")]
        total_files = len(mjo_files)
        
        for idx, filename in enumerate(mjo_files, 1):
            file_counter = f"[{idx}/{total_files}]"
            input_path = os.path.join(input_dir, filename)
            base_name = os.path.splitext(filename)[0]

            print_header(f"处理文件 {file_counter}：{filename}")
            print_debug(f"完整路径：{input_path}")

            try:
                # 执行反汇编
                print_debug("执行命令：")
                cmd_str = f'"{mjdisasm_path}" "{input_path}"'
                print_debug(cmd_str, 2, "▶")

                result = subprocess.run(
                    [mjdisasm_path, input_path],
                    capture_output=True,
                    text=True,
                    check=True,
                    encoding='shift_jis'
                )

                # 记录命令输出
                if result.stdout.strip():
                    print_debug("命令输出：", 2, "↳")
                    print_debug(result.stdout.strip(), 3)

                # 移动生成文件
                moved_files = []
                for ext in [".sjs", ".mjs"]:
                    src = os.path.join(mjdisasm_work_dir, base_name + ext)
                    dest = os.path.join(temp_file_dir, base_name + ext)

                    if os.path.exists(src):
                        shutil.move(src, dest)
                        moved_files.append(dest)
                    else:
                        print_debug(f"未生成 {ext} 文件", 2, "⚠")

                # 处理结果
                if len(moved_files) == 2:
                    result_log['success'].append(filename)
                    print_debug("✓ 成功生成并移动文件", 2, "✔")
                else:
                    raise Exception(f"缺少生成文件，仅找到 {len(moved_files)}/2 个文件")

            except subprocess.CalledProcessError as e:
                error_msg = f"[{e.returncode}] {e.stderr.strip() or '未知错误'}"
                result_log['failed'][filename].append(error_msg)
                print_debug(f"✘ 反汇编失败：{error_msg}", 2, "❗")
            except Exception as e:
                error_msg = str(e)
                result_log['failed'][filename].append(error_msg)
                print_debug(f"⚠ 处理异常：{error_msg}", 2, "❌")

    finally:
        # 生成最终报告
        print_header("最终处理报告")
        
        # 成功文件列表
        print_debug(f"成功文件 ({len(result_log['success'])} 个)", 0, "✔")
        for idx, fname in enumerate(result_log['success'], 1):
            print_debug(f"{idx:02d}. {fname}", 1)
        
        # 失败文件列表
        print_debug(f"\n失败文件 ({len(result_log['failed'])} 个)", 0, "✘")
        for idx, (fname, errors) in enumerate(result_log['failed'].items(), 1):
            print_debug(f"{idx:02d}. {fname}", 1)
            for err in errors:
                print_debug(f"→ {err}", 2)
        
        # 统计信息
        print_debug("\n处理摘要：", 0, "📊")
        print_debug(f"总文件数：{total_files} 个", 1)
        print_debug(f"成功率：{len(result_log['success'])/total_files:.1%}", 1)
        print_debug(f"输出目录：{temp_file_dir}", 1)

# ==== 执行 ====
if __name__ == "__main__":
    try:
        disasm_mjo_files()
    finally:
        press_any_key("按任意键退出程序...")