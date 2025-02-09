import sys
import os

print("✅ conftest.py has been loaded!")

# モジュール読み取り用のパス追加
def append_paths():
    # 現在のパス
    pwd = os.path.dirname(__file__)
    # 2階層上のパスを探索パスに追加（functions用）
    pwd_2up = fr'{pwd}/../../'
    sys.path.append(pwd_2up)
    print(f'append [{pwd_2up}] to path.')
    # MigrationHandlerLayerのパスを探索パスに追加
    layer_path = fr'{pwd_2up}layers/MigrationHandler'
    sys.path.append(layer_path)
    print(f'append [{layer_path}] to path.')

append_paths()
