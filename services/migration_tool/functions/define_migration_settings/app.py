import json
import random

def lambda_handler(event, context):
    # TODO implement
    return {
        'statusCode': 200,
        'body': json.dumps('Hello from Lambda!'),
        'migration_list': [0, 1],
        'continue': 0 == random.randint(0, 1)
    }
