import json
import os
import argparse
from unittest.mock import patch

from get_all_inventory_items.lambda_function import lambda_handler as get_all_handler
from get_inventory_item.lambda_function import lambda_handler as get_item_handler
from add_inventory_item.lambda_function import lambda_handler as add_item_handler
from delete_inventory_item.lambda_function import lambda_handler as delete_item_handler
from get_location_inventory_items.lambda_function import lambda_handler as get_location_handler


def pretty_print(result):
    print(json.dumps(result, indent=2, ensure_ascii=False))


class FakeDynamoDBTable:
    def __init__(self):
        self.items = {}

    def scan(self):
        return {'Items': list(self.items.values())}

    def get_item(self, Key):
        item = self.items.get(Key['id'])
        return {'Item': item} if item else {}

    def put_item(self, Item):
        self.items[Item['id']] = Item
        return {'ResponseMetadata': {'HTTPStatusCode': 200}}

    def delete_item(self, Key, ReturnValues=None):
        item = self.items.pop(Key['id'], None)
        if item:
            return {'Attributes': item}
        return {}

    def query(self, IndexName=None, KeyConditionExpression=None):
        # Very simple simulation: match location_id equality
        location_id = None
        if hasattr(KeyConditionExpression, 'get_expression'):
            expr = KeyConditionExpression.get_expression()
            values = expr.get('values', ())
            if len(values) >= 2:
                location_id = values[1]
        if location_id is None:
            expression_text = str(KeyConditionExpression)
            location_id = int(expression_text.split('=')[-1].strip())
        results = [item for item in self.items.values() if item.get('location_id') == location_id]
        return {'Items': results}


class FakeDynamoDBResource:
    def __init__(self, table):
        self._table = table

    def Table(self, table_name):
        return self._table


def run_tests(mock_mode=False):
    if mock_mode:
        fake_table = FakeDynamoDBTable()
        fake_resource = FakeDynamoDBResource(fake_table)
        patcher = patch('boto3.resource', return_value=fake_resource)
        patcher.start()

    print('=== get_all_inventory_items ===')
    result = get_all_handler({}, None)
    pretty_print(result)

    print('\n=== add_inventory_item ===')
    add_event = {
        'body': json.dumps({
            'name': 'Test Item',
            'description': 'Test description',
            'qty_on_hand': 10,
            'price': 19.99,
            'location_id': 1
        })
    }
    result = add_item_handler(add_event, None)
    pretty_print(result)

    added_item = json.loads(result['body']) if result['statusCode'] == 201 else None
    item_id = added_item['id'] if added_item else 'test-id'

    print('\n=== get_inventory_item ===')
    result = get_item_handler({'pathParameters': {'id': item_id}}, None)
    pretty_print(result)

    print('\n=== get_location_inventory_items ===')
    result = get_location_handler({'pathParameters': {'id': '1'}}, None)
    pretty_print(result)

    print('\n=== delete_inventory_item ===')
    result = delete_item_handler({'pathParameters': {'id': item_id}}, None)
    pretty_print(result)

    if mock_mode:
        patcher.stop()


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Test Lambda function handlers locally.')
    parser.add_argument('--mock', action='store_true', help='Run tests offline using fake DynamoDB.')
    parser.add_argument('--table', default='Inventory', help='DynamoDB table name to use for testing.')
    parser.add_argument('--index', default='Reverse_PK_SK', help='DynamoDB GSI name to use for location queries.')
    args = parser.parse_args()

    os.environ['INVENTORY_TABLE_NAME'] = args.table
    os.environ['LOCATION_INDEX_NAME'] = args.index

    print('Local Lambda function test harness')
    print(f"Using DynamoDB table: {args.table}")
    print(f"Using location index: {args.index}")
    print('Use --mock to run without AWS credentials and without a real DynamoDB table.')
    print()
    run_tests(mock_mode=args.mock)
