from __future__ import unicode_literals, print_function
import unittest
import boto3
import six
import sys
import os
import uuid
from os.path import dirname, join
from moto import mock_dynamodb2

from api.tweet.models import Tweet

class TestModel(unittest.TestCase):
    
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


    @mock_dynamodb2
    def test_create(self):
        self.init()
        t = Tweet()
        content = 'Message one!'
        t.content = content
        result = t.save()
        
        # Did it save?
        assert 'Attributes' in result
        # Is the content what it should be?
        assert t.content == content
        assert result['Attributes']['content'] == content

        # is the date set?
        assert t.created is not None and t.created > 0
        assert result['Attributes']['created'] == t.created

        # is the ID set?
        assert t.id is not None
        assert result['Attributes']['id'] == t.id
    
    @mock_dynamodb2
    def test_create_exception(self):
        self.init()
        t = Tweet()

        with self.assertRaises(ValueError):
            # save without setting content
            t.save()
    
    @mock_dynamodb2
    def test_all(self):
        self.init()
        Tweet(content="Hello World!").save()
        Tweet(content="Rather be using Golang").save()
        Tweet(content="Need a vacation").save()
        Tweet(content="Nap time!").save()
        result = Tweet().all()
        # are all of the results in the list?
        assert len(result) == 4
    
    @mock_dynamodb2
    def test_created_key(self):
        self.init()
        tweet = Tweet()
        # For now, as a simple test, just make sure it's in the last when setting the minus property to 1
        assert tweet.created_key(1) <  tweet.created_key()
    
    @mock_dynamodb2
    def test_whitelist(self):
        self.init()
        tweet = Tweet()
        d = {'content': 'Hello', 'header': 'test', 'fake': 'this', 'id': '1'}
        
        tweet.init_from_dict(d)
        assert tweet.id != 1
        assert tweet.content == 'Hello'
        assert tweet.header == 'test'
        assert 'fake' not in tweet.__dict__ 


if __name__ == '__main__':
    unittest.main()
