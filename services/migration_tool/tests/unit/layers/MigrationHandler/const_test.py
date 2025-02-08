import sys
import os
import pytest

import const as co

@pytest.fixture
def setup():
    # 環境変数の設定
    os.environ['BUCKET_NAME'] = 'hoge'
    os.environ['OBJECT_PATH'] = 'fuga/'
    os.environ['LOCAL_DIRECTORY_ROOT'] = r'c:/tmp/'

# Layerテスト用の関数
@pytest.mark.parametrize(
    "target, expected", [
        ('bucket_name', 'hoge'),
        ('object_path', 'fuga/'),
        ('definition_object_name', '移行定義FMT.xlsx'),
        ('definition_object_key', 'fuga/移行定義FMT.xlsx'),
        ('local_directory_root', r'c:/tmp/')
    ]
)
def test_const_定数が設定されるか(setup, target, expected):
    const = co.Constructor()
    
    # 定数が設定されているかを確認
    assert getattr(const, target) == expected

def test_const_フォルダ名が動的に生成されるか(setup):
    const = co.Constructor()
    
    # 定数が設定されているかを確認
    local_directory_root_length = len(const.local_directory_root + '/')
    folder_name_length = len('folder_') + 36 + len('/') # uuid4
    assert len(const.local_directory_path) == local_directory_root_length + folder_name_length

def test_const_動的にされたフォルダ名が一致しないか(setup):
    const1 = co.Constructor()
    const2 = co.Constructor()
    
    # 異なるフォルダ名が設定されているかを確認
    assert const1.local_directory_path != const2.local_directory_path

def test_const_ローカルの定義ファイルのパスが設定されるか(setup):
    const = co.Constructor()
    local_definition_file_path = f'{const.local_directory_path}{const.definition_object_name}'
    
    # 異なるフォルダ名が設定されているかを確認
    assert const.local_definition_file_path == local_definition_file_path
