import pytest
import os
from contextlib import contextmanager

import const as co
import utils

@pytest.fixture
def setup():
    # 環境変数の設定
    os.environ['BUCKET_NAME'] = 'siruko-cloudformation-templetes'
    os.environ['OBJECT_PATH'] = 'migration-tool/unittest/'
    os.environ['LOCAL_DIRECTORY_ROOT'] = r'c:/tmp/'
    os.environ['PYTEST_LOCAL'] = 'LOCAL'
    # lockファイル
    const = co.Constructor()
    os.makedirs(const.local_directory_path, exist_ok=False)
    lock_file = f"{const.object_path}hoge.lock"
    lock_file_local = f"{const.local_directory_path}hoge.lock"
    class Setup:
      def __init__(self):
          self.const = const
          self.lock_file = lock_file
          self.lock_file_local = lock_file_local
    return Setup()

def test_is_local_ローカル環境の場合():
    os.environ['PYTEST_LOCAL'] = 'LOCAL'
    assert utils.is_local() == True

def test_utils_ローカル環境でlockファイルが作成削除されること(setup):
    lock_file = setup.lock_file_local
    assert utils.is_local() == True
    assert utils.is_exists_file('bucket', lock_file) == False # 初期状態はファイルなし
    utils.create_lock_file('bucket', lock_file) # ファイルを生成
    assert utils.is_exists_file('bucket', lock_file) == True # 生成されたことを確認
    utils.delete_lock_file('bucket', lock_file) # 削除
    assert utils.is_exists_file('bucket', lock_file) == False # ファイルがないことを確認

def test_utils_AWS環境でlockファイルが作成削除されること(setup):
    bucket_name = setup.const.bucket_name
    lock_file = setup.lock_file
    del os.environ['PYTEST_LOCAL']
    assert utils.is_local() == False
    assert utils.is_exists_file(bucket_name, lock_file) == False # 初期状態はファイルなし
    utils.create_lock_file(bucket_name, lock_file) # ファイルを生成
    assert utils.is_exists_file(bucket_name, lock_file) == True # 生成されたことを確認
    utils.delete_lock_file(bucket_name, lock_file) # 削除
    assert utils.is_exists_file(bucket_name, lock_file) == False # ファイルがないことを確認
