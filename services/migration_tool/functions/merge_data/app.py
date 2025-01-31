from handler import MigrationHandler

def handler(event, context):

    target = event
    print(f'target: {target}')

    migration_handler = MigrationHandler()
    setting = migration_handler.get_setting(target)
    migration_handler.run(setting)
    