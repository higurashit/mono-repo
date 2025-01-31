import os
from handler import MigrationHandler

def handler(event, context):

    # 移行定義のパスを環境変数から取得
    bucket_name = os.environ.get("BUCKET_NAME")
    file_path = f'{os.environ.get("WORK_DIR_KEY")}移行定義FMT.xlsx'
    print(f"event: {event}, bucket_name: {bucket_name}, file_path: {file_path}")

    # 移行対象のキー配列を取得
    migration_handler = MigrationHandler(file_path=f'{bucket_name}{file_path}')
    definitions:dict = migration_handler.load_definitions()
    migration_targets = definitions.keys()

    return {
        'targets': migration_targets
    }