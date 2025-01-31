import os
from handler import MigrationHandler

def handler(event, context):

    # 移行定義のパスを環境変数から取得
    print(f"event: {event}")

    # 移行対象のキー配列を取得
    migration_handler = MigrationHandler()
    definitions:dict = migration_handler.load_definitions()
    migration_targets = [key for key in definitions.keys()]
    print(f"migration_targets: {migration_targets}")

    return {
        'targets': migration_targets
    }