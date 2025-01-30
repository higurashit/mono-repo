from handler import MigrationHandler

if __name__ == "__main__":
    handler = MigrationHandler()

    # Lambda 1 つ目
    migration_settings = handler.get_settings()

    # Lambda 2 つ目（Mapステート）
    for setting in migration_settings:
        handler.run(setting)
