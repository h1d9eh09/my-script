import psutil
import sys
import os

def is_admin():
    try:
        return os.getuid() == 0  
    except AttributeError:
        import ctypes
        return ctypes.windll.shell32.IsUserAnAdmin() != 0

def run_as_admin():
    import ctypes
    ctypes.windll.shell32.ShellExecuteW(
        None, "runas", sys.executable, " ".join(sys.argv), None, 1
    )

if not is_admin():
    print("提权中...")
    run_as_admin()
    sys.exit()

# 获取 CPU 核心数（逻辑核心）
cpu_count = psutil.cpu_count(logical=True)
if not cpu_count:
    cpu_count = 1
last_core = cpu_count - 1

# 使用位掩码设置CPU相关性
# 计算只绑定到最后一个CPU的位掩码
affinity_mask = 1 << last_core  # 将1左移last_core位

target_names = ["SGuardSvc64.exe", "SGuard64.exe"]

for proc in psutil.process_iter(['pid', 'name']):
    try:
        if proc.info['name'] in target_names:
            p = psutil.Process(proc.info['pid'])
            # 设置优先级为低
            p.nice(psutil.IDLE_PRIORITY_CLASS)
            # 设置CPU相关性到最后一个核心
            p.cpu_affinity([last_core])  # 使用CPU编号列表
            print(f"已处理 {proc.info['name']} (PID: {proc.info['pid']}) -> 相关性: CPU{last_core}, 优先级: 低")
    except (psutil.NoSuchProcess, psutil.AccessDenied, OSError) as e:
        print(f"无法处理 {proc.info['name']} (PID: {proc.info['pid']}): {e}")

input("\n完成，按回车退出...")