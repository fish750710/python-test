import subprocess
import sys
from multiprocessing import Process
import argparse

def run_flask(port=5000, host="0.0.0.0"):
    subprocess.run([sys.executable, "-m", "flask", "run", f"--port={port}", f"--host={host}"])

def run_task_runner():
    subprocess.run([sys.executable, "task_runner.py"])

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="執行 Flask 應用程式和任務執行器")
    # 添加命令行選項
    parser.add_argument("--port", type=int, default=5000, help="Flask 應用程式的端口 (預設: 5000)")
    parser.add_argument("--host", type=str, default="0.0.0.0", help="")
    # 解析命令行
    args = parser.parse_args()

    # 啟動 Flask 應用程式
    # 使用方式: python run.py --port 5000 --host 192.168.100.40
    # 或直接執行 python run.py 使用預設值
    flask_process = Process(target=run_flask, args=(args.port, args.host))
    task_runner_process = Process(target=run_task_runner)

    flask_process.start()
    task_runner_process.start()

    # 等待 Flask 應用程式和任務執行器結束
    flask_process.join()
    task_runner_process.join()
