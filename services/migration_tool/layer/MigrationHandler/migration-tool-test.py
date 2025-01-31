from handler import MigrationHandler

# Layerテスト用の関数
def statemachine_handler():

    # lambda1
    migration_targets: list[str] = handler1()

    # lambda2 (Map State)
    for target in migration_targets:
        handler2(target)

def handler1():

    # testsフォルダの移行定義を参照
    directory_path = "../../tests/unit/data/"
    file_path = f"{directory_path}移行定義FMT.xlsx"
    
    migration_handler = MigrationHandler(file_path=file_path)
    definitions:dict = migration_handler.load_definitions()
    migration_targets = definitions.keys()

    # シート名配列を返却
    return migration_targets

def handler2(target):

    # testsフォルダの移行定義を参照
    directory_path = "../../tests/unit/data/"
    file_path = f"{directory_path}移行定義FMT.xlsx"

    migration_handler = MigrationHandler(file_path=file_path)
    setting: tuple[dict, list[dict]] = migration_handler.get_setting(target)

    _, srcs = setting
    for src in srcs:
        src["input"]["path"] = f'{directory_path}{src["input"]["path"]}' 
        # print(src["input"]["path"])

    migration_handler.run(setting)


if __name__ == "__main__":
    statemachine_handler()