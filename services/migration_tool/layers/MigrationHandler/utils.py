import boto3
import botocore.exceptions
import time
import os
from contextlib import contextmanager

DEBUG = True
s3 = boto3.client('s3', region_name='ap-northeast-1')

@contextmanager
def time_log(msg: str):
    print(f"{msg} - 開始")
    st_tm = time.time()
    yield
    ed_tm = time.time()
    print(f"{msg} - 終了: 所要時間 {ed_tm - st_tm:.3f} 秒")

def is_local():
    if os.getenv('PYTEST_LOCAL') == None:
        return False
    return True

def debug_print(data):
    if DEBUG:
        print(data)

def check_lock_file_is_exists(bucket_name, file_path, retry=0, interval_sec=3):
  while True:
    is_exists = is_exists_file(bucket_name, file_path)
    if is_exists:
      print(f"{file_path} がロック中です。{interval_sec}秒後に再試行...（{retry + 1}回目）")
      time.sleep(interval_sec)
      retry += 1
    else:
      print(f'Lock file is NOT exists. OK.')
      return

def check_lock_file_is_not_exists(bucket_name, file_path):
  while True:
    is_exists = is_exists_file(bucket_name, file_path)
    if not is_exists:
      msg = f"ロックファイル [{file_path}] が存在しません。"
      raise Exception(msg)
    else:
       print(f'Lock file is exists. OK.')
       return

def is_exists_file(bucket_name, file_path):
  try:
    if is_local():
      if not os.path.isfile(file_path):
         return False
    else:
      s3.head_object(Bucket=bucket_name, Key=file_path)
    return True
  except botocore.exceptions.ClientError as e:
    if e.response["Error"]["Code"] == "404": # Not Found.
      return False
    print(e.response)
    raise e
  except Exception as e:
    print(e.response)
    raise e

def create_lock_file(bucket_name, file_path, body="lock"):
    check_lock_file_is_exists(bucket_name, file_path)
    # lockファイルを作成    
    if is_local():
      with open(file_path, "w") as f:
        print(f'Create lock file [{file_path}].')
        f.write("lock")
    else:
      print(f'Create lock file [s3://{bucket_name}/{file_path}].')
      s3.put_object(Bucket=bucket_name, Key=file_path, Body=body)

def delete_lock_file(bucket_name, file_path):
    check_lock_file_is_not_exists(bucket_name, file_path)
    # lockファイルを削除
    if is_local():
      print(f'Delete lock file [{file_path}].')
      os.remove(file_path)
    else:
      print(f'Delete lock file [s3://{bucket_name}/{file_path}].')
      s3.delete_object(Bucket=bucket_name, Key=file_path)
