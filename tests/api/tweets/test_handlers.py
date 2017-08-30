from __future__ import unicode_literals, print_function
import unittest
import boto3
import six
import sys
import os
import uuid
import json
from os.path import dirname, join
from moto import mock_dynamodb2

from api.tweet import get, post

class TestAPIFunctions(unittest.TestCase):

    def init(self):
        os.environ['AWS_DEFAULT_REGION'] = 'us-east-2'
        dynamodb = boto3.resource('dynamodb', region_name='us-east-2')
        table_name = os.getenv('TWEET_TABLE', 'tweets')
        
        self.table = dynamodb.create_table(
            TableName=table_name,
            KeySchema=[
                {
                    # Represents the YYYYMMDD 
                    # This is used to query all tweets for a given day
                    'AttributeName': 'created_key',
                    'KeyType': 'HASH'  #Partition key
                },
                {
                    'AttributeName': 'created',
                    'KeyType': 'RANGE'  #Sort key
                }
            ],
            AttributeDefinitions=[
                {
                    'AttributeName': 'id',
                    'AttributeType': 'S'
                },
                {
                    'AttributeName': 'content',
                    'AttributeType': 'S'
                },
                {
                    'AttributeName': 'created',
                    'AttributeType': 'N'
                },
                {
                    'AttributeName': 'created_key',
                    'AttributeType': 'N'
                },
                {
                    'AttributeName': 'header',
                    'AttributeType': 'S'
                }
            ],
            ProvisionedThroughput={
                'ReadCapacityUnits': 10,
                'WriteCapacityUnits': 10
            }
        )

        # Wait until the table exists.
        self.table.meta.client.get_waiter('table_exists').wait(TableName=table_name)
        assert self.table.table_status == 'ACTIVE'

    def tearDown(self):
        pass

    @mock_dynamodb2
    def test_post(self):
        self.init()            
        r1 = post.handler({'body': '''{"content":"Hello", "header":"THIS"}'''}, {})
        r2 = post.handler({'body': '''{"content":"Hello2", "header":"THAT"}'''}, {})
        
        # HTTP status of 200?
        assert r1['statusCode'] == '200'
        assert r2['statusCode'] == '200'

        b1 = json.loads(r1['body'])
        b2 = json.loads(r2['body'])

        # Are the results correct?
        assert 'content' in b1 and 'header' in b1
        assert 'content' in b2 and 'header' in b2
        assert b1['content'] == 'Hello' and b1['header'] == 'THIS'
        assert b2['content'] == 'Hello2' and b2['header'] == 'THAT'
        
    @mock_dynamodb2
    def test_post_failed(self):
        self.init()            
        result = post.handler({'body': '{}'}, {})
        # HTTP status of 400?
        assert result['statusCode'] == '400'
        # Are the results correct?
        assert 'error' in result['body'].lower()


    
    @mock_dynamodb2
    def test_get(self):
        self.init()
        r1 = post.handler({'body': '''{"content":"Hello", "header":"THIS"}'''}, {})
        r2 = post.handler({'body': '''{"content":"Hello2", "header":"THAT"}'''}, {})
        result = get.handler({}, {})

        assert result['statusCode'] == '200'
        body = json.loads(result['body'])
        assert len(body) == 2
        assert body[0]['content'] == 'Hello'
        assert body[1]['content'] == 'Hello2' 

  

if __name__ == '__main__':
    unittest.main()
