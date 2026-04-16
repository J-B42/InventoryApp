import os
import boto3
import json
import ulid
from decimal import Decimal

# v1.1 - Deployed via fixed GitHub Actions
TABLE_NAME = os.environ.get('INVENTORY_TABLE_NAME', 'Inventory')

def _generate_ulid() -> str:
    # Support common ulid package variants used in Lambda deployments.
    if hasattr(ulid, 'new'):
        return str(ulid.new())
    if hasattr(ulid, 'ULID'):
        return str(ulid.ULID())
    if hasattr(ulid, 'ulid'):
        return str(ulid.ulid())
    raise RuntimeError('ULID library does not expose a supported generator')

def lambda_handler(event, context):
    # Initialize DynamoDB resource
    dynamodb = boto3.resource('dynamodb')
    table = dynamodb.Table(TABLE_NAME)
    
    try:
        # Parse request body
        body = json.loads(event['body'])
        
        # Validate required fields
        required_fields = ['name', 'description', 'qty_on_hand', 'price', 'location_id']
        for field in required_fields:
            if field not in body:
                return {
                    'statusCode': 400,
                    'body': json.dumps({'error': f'Missing required field: {field}'}),
                    'headers': {
                        'Content-Type': 'application/json'
                    }
                }
        
        # Generate ULID for item ID
        item_id = _generate_ulid()
        
        # Create item dictionary
        item = {
            'id': item_id,
            'name': body['name'],
            'description': body['description'],
            'qty_on_hand': int(body['qty_on_hand']),
            'price': Decimal(str(body['price'])),
            'location_id': int(body['location_id'])
        }
        
        # Put item in DynamoDB
        table.put_item(Item=item)
        
        # Return created item
        return {
            'statusCode': 201,
            'body': json.dumps(item, default=str),  # Convert Decimal to string
            'headers': {
                'Content-Type': 'application/json'
            }
        }
    except json.JSONDecodeError:
        return {
            'statusCode': 400,
            'body': json.dumps({'error': 'Invalid JSON in request body'}),
            'headers': {
                'Content-Type': 'application/json'
            }
        }
    except ValueError as e:
        return {
            'statusCode': 400,
            'body': json.dumps({'error': f'Invalid data type: {str(e)}'}),
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
