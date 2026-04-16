import os
import boto3
import json
from boto3.dynamodb.conditions import Key

# v1.1 - Deployed via fixed GitHub Actions
TABLE_NAME = os.environ.get('INVENTORY_TABLE_NAME', 'Inventory')
LOCATION_INDEX_NAME = os.environ.get('LOCATION_INDEX_NAME', 'Reverse_PK_SK')

def lambda_handler(event, context):
    # Initialize DynamoDB resource
    dynamodb = boto3.resource('dynamodb')
    table = dynamodb.Table(TABLE_NAME)
    
    try:
        # Get location ID from path parameters
        location_id = int(event['pathParameters']['id'])
    except KeyError:
        # Missing path parameter
        return {
            'statusCode': 400,
            'body': json.dumps({'error': 'Missing location ID'}),
            'headers': {
                'Content-Type': 'application/json'
            }
        }
    except ValueError:
        return {
            'statusCode': 400,
            'body': json.dumps({'error': 'Invalid location ID format'}),
            'headers': {
                'Content-Type': 'application/json'
            }
        }

    try:
        # Query the GSI for items in this location
        response = table.query(
            IndexName=LOCATION_INDEX_NAME,
            KeyConditionExpression=Key('location_id').eq(location_id)
        )
        
        items = response['Items']
        
        # Return the items
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
