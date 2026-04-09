import boto3
import json
import ulid

def lambda_handler(event, context):
    # Initialize DynamoDB resource
    dynamodb = boto3.resource('dynamodb')
    table = dynamodb.Table('Inventory')
    
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
        item_id = str(ulid.ulid())
        
        # Create item dictionary
        item = {
            'id': item_id,
            'name': body['name'],
            'description': body['description'],
            'qty_on_hand': int(body['qty_on_hand']),
            'price': float(body['price']),
            'location_id': int(body['location_id'])
        }
        
        # Put item in DynamoDB
        table.put_item(Item=item)
        
        # Return created item
        return {
            'statusCode': 201,
            'body': json.dumps(item),
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
