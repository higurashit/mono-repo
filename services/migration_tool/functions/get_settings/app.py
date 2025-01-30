from handler import MigrationHandler

def handler(event, context):

    migration_handler = MigrationHandler()
    migration_settings = migration_handler.get_settings()

    return {
        'migration_settings': migration_settings
    }