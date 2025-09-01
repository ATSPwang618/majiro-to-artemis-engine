import os
import subprocess
import sys

# 配置区域（根据实际情况修改）===========================================
MJCRYPT_PATH = r"C:\Users\Administrator\Desktop\水仙\1.majiro-解密mjo\mjcrypt.exe"
SOURCE_DIR = r"C:\Users\Administrator\Desktop\水仙\1.majiro-解密mjo\原始mjo文件"
DEST_DIR = r"C:\Users\Administrator\Desktop\水仙\1.majiro-解密mjo\解密mjo文件"
# ======================================================================

def print_colored(text, color_code):
    """带颜色的命令行输出"""
    sys.stdout.write(f"\033[{color_code}m{text}\033[0m\n")

def process_files():
    # 创建目标目录
    os.makedirs(DEST_DIR, exist_ok=True)
    
    # 获取文件列表
    try:
        files = [f for f in os.listdir(SOURCE_DIR) if f.lower().endswith('.mjo')]
    except FileNotFoundError:
        print_colored(f"错误：源目录不存在 {SOURCE_DIR}", 31)
        return

    total = len(files)
    success = 0
    failures = []

    print_colored(f"▶ 开始批量处理，共发现 {total} 个.mjo文件", 36)
    print("=" * 60)

    for idx, filename in enumerate(files, 1):
        src_path = os.path.join(SOURCE_DIR, filename)
        dest_path = os.path.join(DEST_DIR, f"decrypted_{filename}")

        # 显示进度
        progress = f"[{idx}/{total}]".ljust(10)
        print(f"{progress} 正在处理: {filename}...", end='', flush=True)

        try:
            # 执行解密命令
            result = subprocess.run(
                [MJCRYPT_PATH, src_path, dest_path],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                creationflags=subprocess.CREATE_NO_WINDOW
            )

            if result.returncode == 0:
                print_colored(" [成功]", 32)
                success += 1
            else:
                error_msg = result.stderr.strip() or "未知错误"
                print_colored(f" [失败] {error_msg}", 31)
                failures.append((filename, error_msg))

        except Exception as e:
            print_colored(f" [异常] {str(e)}", 31)
            failures.append((filename, str(e)))

    # 打印汇总报告
    print("\n" + "=" * 60)
    print_colored(f"处理完成：{success} 成功 / {len(failures)} 失败", 36 if failures else 32)
    
    if failures:
        print_colored("\n失败详情：", 33)
        for i, (file, err) in enumerate(failures, 1):
            print(f"{i}. {file}: {err}")

if __name__ == "__main__":
    process_files()
    input("\n按 Enter 键退出...")