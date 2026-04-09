import boto3
import json
from boto3.dynamodb.conditions import Key

def lambda_handler(event, context):
    # Initialize DynamoDB resource
    dynamodb = boto3.resource('dynamodb')
    table = dynamodb.Table('Inventory')
    
    try:
        # Get location ID from path parameters
        location_id = int(event['pathParameters']['id'])
        
        # Query the GSI for items in this location
        response = table.query(
            IndexName='LocationIndex',  # Assuming this is the GSI name
            KeyConditionExpression=Key('location_id').eq(location_id)
        )
        
        items = response['Items']
        
        # Return the items
        return {
            'statusCode': 200,
            'body': json.dumps(items),
            'headers': {
                'Content-Type': 'application/json'
            }
        }
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
    except Exception as e:
        # Return error response
        return {
            'statusCode': 500,
            'body': json.dumps({'error': str(e)}),
            'headers': {
                'Content-Type': 'application/json'
            }
        }
