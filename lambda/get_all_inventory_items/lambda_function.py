import os
import boto3
import json

TABLE_NAME = os.environ.get('INVENTORY_TABLE_NAME', 'Inventory')

def lambda_handler(event, context):
    # Initialize DynamoDB resource
    dynamodb = boto3.resource('dynamodb')
    table = dynamodb.Table(TABLE_NAME)
    
    try:
        # Scan the table to get all items
        response = table.scan()
        items = response['Items']
        
        # Return successful response
        return {
            'statusCode': 200,
            'body': json.dumps(items, default=str),
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
