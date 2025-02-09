import os
import pytest
from utils import is_local
from functions.get_targets.app import handler as get_targets

@pytest.fixture
def setup():
    # 環境変数の設定
    os.environ['BUCKET_NAME'] = 'siruko-cloudformation-templetes'
    os.environ['OBJECT_PATH'] = 'migration-tool/unittest/'
    os.environ['LOCAL_DIRECTORY_ROOT'] = r'c:/tmp/'
    os.environ['PYTEST_LOCAL'] = 'LOCAL'

# Layerテスト用の関数
def test_get_targets_ローカルファイルから移行対象が取得できているか(setup):
    assert is_local() == True
    
    event = None
    context = None
    f1result = get_targets(event, context)
    print(f'f1result: {f1result}')
    assert "targets" in f1result

def test_get_targets_S3から移行対象が取得できているか(setup):
    del os.environ['PYTEST_LOCAL']
    assert is_local() == False

    event = None
    context = None
    f1result = get_targets(event, context)
    print(f'f1result: {f1result}')
    assert "targets" in f1result