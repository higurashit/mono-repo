import time
import os
from contextlib import contextmanager

DEBUG = True

@contextmanager
def time_log(msg: str):
    print(f"{msg} - 開始")
    st_tm = time.time()
    yield
    ed_tm = time.time()
    print(f"{msg} - 終了: 所要時間 {ed_tm - st_tm:.3f} 秒")

def debug_print(data):
    if DEBUG:
        print(data)

def check_lock_file(file_path, retry=0, interval_sec=3):
    while os.path.isfile(file_path):
        print(f"{file_path} がロック中です。{interval_sec}秒後に再試行...（{retry + 1}回目）")
        time.sleep(interval_sec)
        retry += 1

def create_lock_file(file_path):
    with open(file_path, "w") as f:
        f.write("lock")

def delete_lock_file(file_path):
    os.remove(file_path)
