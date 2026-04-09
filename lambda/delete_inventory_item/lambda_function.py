import boto3
import json

def lambda_handler(event, context):
    # Initialize DynamoDB resource
    dynamodb = boto3.resource('dynamodb')
    table = dynamodb.Table('Inventory')
    
    try:
        # Get item ID from path parameters
        item_id = event['pathParameters']['id']
        
        # Delete the item from DynamoDB
        response = table.delete_item(
            Key={'id': item_id},
            ReturnValues='ALL_OLD'  # Return the deleted item if it existed
        )
        
        if 'Attributes' in response:
            # Item was deleted
            return {
                'statusCode': 204,
                'body': '',
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
