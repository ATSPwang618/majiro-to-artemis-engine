import os
import msvcrt
from datetime import datetime

# ==== 配置路径 ====
temp_dir = r"C:\Users\Administrator\Desktop\水仙\2.majiro-mjo脚本解析\temp"

# ==== 辅助函数 ====
def press_any_key(prompt="按任意键开始转换..."):
    """等待用户按键"""
    print(f"\n{prompt}", end='', flush=True)
    msvcrt.getch()
    print("\n" + "=" * 50)

def print_debug(info, level=1):
    """分级调试信息输出"""
    prefixes = {
        1: "[INFO] ",
        2: "  [DEBUG] ",
        3: "    [ERROR] "
    }
    print(f"{prefixes.get(level, '')}{info}")

# ==== 转码函数 ====
def convert_sjs_to_utf8(directory):
    start_time = datetime.now()
    print_debug(f"🔍 开始扫描目录：{directory}", 1)
    
    total_files = 0
    converted = 0
    failed_files = []

    # 遍历目录
    for filename in os.listdir(directory):
        if not filename.lower().endswith(".sjs"):
            continue
            
        total_files += 1
        file_path = os.path.join(directory, filename)
        
        print_debug(f"处理文件 [{total_files}]: {filename}", 2)
        print_debug(f"完整路径：{file_path}", 2)

        try:
            # 读取原始文件
            with open(file_path, "r", encoding="shift_jis") as f:
                content = f.read()
                print_debug(f"读取成功，文件大小：{len(content)} 字符", 2)

            # 写入转换后内容
            with open(file_path, "w", encoding="utf-8") as f:
                f.write(content)
                print_debug("转换写入成功", 2)
                converted += 1

        except UnicodeDecodeError as e:
            error_msg = f"编码解析失败：{str(e)}"
            print_debug(error_msg, 3)
            failed_files.append((filename, error_msg))
        except Exception as e:
            error_msg = f"未知错误：{str(e)}"
            print_debug(error_msg, 3)
            failed_files.append((filename, error_msg))

    # 生成报告
    print("\n" + "=" * 50)
    print_debug(f"🕒 耗时：{datetime.now() - start_time}", 1)
    print_debug(f"📊 统计：", 1)
    print_debug(f"扫描文件总数：{total_files} 个", 1)
    print_debug(f"成功转换：{converted} 个", 1)
    print_debug(f"失败文件：{len(failed_files)} 个", 1)
    
    if failed_files:
        print_debug("\n❌ 失败详情：", 1)
        for idx, (fname, reason) in enumerate(failed_files, 1):
            print_debug(f"{idx}. {fname}: {reason}", 1)

# ==== 执行 ====
if __name__ == "__main__":
    print("\n=== SJS 文件编码转换工具 ===")
    print_debug(f"目标目录：{temp_dir}", 1)
    print_debug(f"操作类型：Shift-JIS → UTF-8", 1)
    
    press_any_key()
    
    try:
        convert_sjs_to_utf8(temp_dir)
    except FileNotFoundError:
        print_debug(f"错误：目录不存在 {temp_dir}", 3)
    except Exception as e:
        print_debug(f"程序异常：{str(e)}", 3)
    
    input("\n按 Enter 键退出...")