import sys
import os

# Layerテスト用の関数
def statemachine_handler():
    # テスト準備
    append_paths()
    set_environs()
    # テスト対象の関数をインポート
    from functions.get_targets.app import handler as get_targets
    from functions.merge_data.app import handler as merge_data

    # F1
    event = None
    context = None
    f1result = get_targets(event, context)
    print(f'f1result: {f1result}')

    # Map
    targets = f1result['targets']
    for target in targets:
        # F2
        event = target
        context = None
        merge_data(event, context)




# モジュール読み取り用のパス追加
def append_paths():
    # 現在のパス
    pwd = os.path.dirname(__file__)
    # 2階層上のパスを探索パスに追加（functions用）
    pwd_2up = fr'{pwd}/../../'
    sys.path.append(pwd_2up)
    print(f'append [{pwd_2up}] to path.')
    # MigrationHandlerLayerのパスを探索パスに追加
    layer_path = fr'{pwd_2up}/layer/MigrationHandler'
    sys.path.append(layer_path)
    print(f'append [{layer_path}] to path.')

# 試験用の環境変数設定
def set_environs():
    # 環境変数の設定
    os.environ['BUCKET_NAME'] = 'siruko-cloudformation-templetes'
    os.environ['OBJECT_PATH'] = 'migration-tool/unittest/'
    os.environ['LOCAL_DIRECTORY_ROOT'] = r'c:/tmp/'

if __name__ == "__main__":
    statemachine_handler()