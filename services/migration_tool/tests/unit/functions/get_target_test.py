import sys
import os

from functions.get_targets.app import handler as get_targets

# Layerテスト用の関数
def test_get_targets_移行対象が取得できているか():
    event = None
    context = None
    f1result = get_targets(event, context)
    print(f'f1result: {f1result}')
    assert "targets" in f1result