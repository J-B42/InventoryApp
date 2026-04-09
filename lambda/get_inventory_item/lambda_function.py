import os
import boto3
import json
from boto3.dynamodb.conditions import Attr

TABLE_NAME = os.environ.get('INVENTORY_TABLE_NAME', 'Inventory')

def lambda_handler(event, context):
    # Initialize DynamoDB resource
    dynamodb = boto3.resource('dynamodb')
    table = dynamodb.Table(TABLE_NAME)
    
    try:
        # Get item ID from path parameters
        item_id = event['pathParameters']['id']
        
        # Scan for the item by id (since id is part of composite key)
        response = table.scan(
            FilterExpression=Attr('id').eq(item_id)
        )
        
        items = response['Items']
        if items:
            # Return the first (and should be only) item
            return {
                'statusCode': 200,
                'body': json.dumps(items[0], default=str),
                'headers': {
                    'Content-Type': 'application/json'
                }
            }
        else:
            # Item not found
            return {
                'statusCode': 404,
                'body': json.dumps({'error': 'Item not found'}),
                'headers': {
                    'Content-Type': 'application/json'
                }
            }
    except KeyError:
        # Missing path parameter
        return {
            'statusCode': 400,
            'body': json.dumps({'error': 'Missing item ID'}),
            'headers': {
                'Content-Type': 'application/json'
            }
        }
    except Exception as e:
        # Return error response
        return {
            'statusCode': 500,
            'body': json.dumps({'error': str(e)}),
            'headers': {
                'Content-Type': 'application/json'
            }
        }
