from handler import MigrationHandler

def handler(event, context):

    setting = event["migration_setting"]

    migration_handler = MigrationHandler()
    migration_handler.run(setting)
    