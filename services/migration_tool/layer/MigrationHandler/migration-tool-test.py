from handler import MigrationHandler

# Layerテスト用の関数
def handler(event, context):

    # testsフォルダの移行定義を参照
    directory_path = "../../tests/unit/data/"
    migration_handler = MigrationHandler(file_path=f"{directory_path}移行定義FMT.xlsx")
    migration_settings = migration_handler.get_settings()

    for setting in migration_settings:
        _, srcs = setting
        for src in srcs:
            src["input"]["path"] = f'{directory_path}{src["input"]["path"]}' 
            print(src["input"]["path"])
        migration_handler.run(setting)

if __name__ == "__main__":
    handler(None, None)