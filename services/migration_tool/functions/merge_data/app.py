import json
import random

def handler(event, context):
    # TODO implement
    return {
        'continue': 0 == random.randint(0, 1)
    }
