import os
import boto3
import json
from boto3.dynamodb.conditions import Attr

# v1.1 - Deployed via fixed GitHub Actions
TABLE_NAME = os.environ.get('INVENTORY_TABLE_NAME', 'Inventory')

def lambda_handler(event, context):
    # Initialize DynamoDB resource
    dynamodb = boto3.resource('dynamodb')
    table = dynamodb.Table(TABLE_NAME)
    
    try:
        # Get item ID from path parameters
        item_id = event['pathParameters']['id']
        
        # Scan for the item by id to find it first
        scan_response = table.scan(
            FilterExpression=Attr('id').eq(item_id)
        )
        
        items = scan_response['Items']
        if not items:
            return {
                'statusCode': 404,
                'body': json.dumps({'error': 'Item not found'}),
                'headers': {
                    'Content-Type': 'application/json'
                }
            }
        
        # Get the full key (id + location_id)
        item = items[0]
        key = {'id': item['id'], 'location_id': item['location_id']}
        
        # Delete the item
        table.delete_item(Key=key)
        
        return {
            'statusCode': 204,
            'body': '',
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
